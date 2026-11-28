"""IA de netteté RAPIDE : même modèle Real-ESRGAN (general-x4v3, BSD-3) que agrandir.py, mais avec OpenVINO (Intel, Apache 2.0),
plusieurs images en parallèle et, avec --int8, un calcul en précision réduite calibré sur la vidéo (image identique à l'œil,
PSNR 45 dB). Mesuré le 28/11/2026 sur une source 720x1280 : torch 3,3 s/image -> OpenVINO 1,66 -> OpenVINO int8 environ 1,2.
Usage : python3 agrandir_rapide.py <entree.mp4> <sortie.mp4> [--taille 1080x1920] [--int8] [--debut-ia N]
  --debut-ia N : images avant N simplement agrandies (lanczos), par exemple un début qui sera coupé.
  Reprise : morceaux de 1000 images dans <sortie>_morceaux/ ; relancer la même commande reprend où ça s'est arrêté.
Installation : bash installer.sh (modèle dans ~/.cache/sr) puis pip install openvino nncf opencv-python-headless."""
import argparse,os,subprocess,sys,time,json,numpy as np,cv2
import openvino as ov
P=argparse.ArgumentParser();P.add_argument('entree');P.add_argument('sortie');P.add_argument('--taille',default='1080x1920')
P.add_argument('--int8',action='store_true');P.add_argument('--debut-ia',type=int,default=0);A=P.parse_args()
TW,TH=map(int,A.taille.split('x'));C=os.path.expanduser('~/.cache/sr');os.makedirs(os.path.join(C,'ov'),exist_ok=True)
pr=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v','-count_packets','-show_entries','stream=width,height,r_frame_rate,nb_read_packets','-of','json',A.entree],capture_output=True,text=True).stdout)['streams'][0]
w,h,N=pr['width'],pr['height'],int(pr['nb_read_packets']);num,den=map(int,pr['r_frame_rate'].split('/'));fps=num/den
def lire(a,b):
    p=subprocess.run(['ffmpeg','-v','error','-i',A.entree,'-vf',f"select='between(n\\,{a}\\,{b})'",'-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    return np.frombuffer(p,np.uint8).reshape(-1,h,w,3)
xml=os.path.join(C,'ov','srvgg.xml')
if not os.path.exists(xml):  # conversion du modèle PyTorch (une fois)
    import torch;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)));from sr import charge
    m=charge('general').float().to(memory_format=torch.contiguous_format)
    ov.save_model(ov.convert_model(m,example_input=torch.rand(1,3,64,64),input=[(1,3,-1,-1)]),xml)
core=ov.Core();modele=xml
if A.int8:  # calibration sur 16 morceaux de la vidéo elle-même
    import nncf
    q8=A.sortie+'_int8.xml'
    if not os.path.exists(q8):
        rng=np.random.default_rng(0);cal=[]
        for k in np.linspace(0,N-1,16).astype(int):
            f=lire(k,k)[0];y=rng.integers(0,max(1,h-256));x=rng.integers(0,max(1,w-256))
            cal.append((f[y:y+256,x:x+256].astype(np.float32)/255).transpose(2,0,1)[None].copy())
        ov.save_model(nncf.quantize(core.read_model(xml),nncf.Dataset(cal),subset_size=len(cal),fast_bias_correction=True),q8)
    modele=q8
cm=core.compile_model(modele,'CPU',{'INFERENCE_PRECISION_HINT':'bf16','PERFORMANCE_HINT':'THROUGHPUT'});NR=cm.get_property('OPTIMAL_NUMBER_OF_INFER_REQUESTS')
D=A.sortie+'_morceaux';os.makedirs(D,exist_ok=True);CH=1000;t0=time.time()
for a in range(0,N,CH):
    b=min(N,a+CH)-1;out=os.path.join(D,f'm{a:06d}.mp4')
    if os.path.exists(out):continue
    tmp=out+'.part.mp4'
    wr=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{TW}x{TH}','-r',str(fps),'-i','-','-c:v','libx264','-crf','14','-preset','veryfast','-pix_fmt','yuv420p',tmp],stdin=subprocess.PIPE)
    rd=subprocess.Popen(['ffmpeg','-v','error','-i',A.entree,'-vf',f"select='between(n\\,{a}\\,{b})'",'-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    prets={};suivant=[0]
    def fini(req,i):prets[i]=cv2.resize(np.clip(req.get_output_tensor(0).data[0].transpose(1,2,0)*255+0.5,0,255).astype(np.uint8),(TW,TH),interpolation=cv2.INTER_AREA)
    q=ov.AsyncInferQueue(cm,NR);q.set_callback(fini)
    def vide():
        while suivant[0] in prets:wr.stdin.write(prets.pop(suivant[0]).tobytes());suivant[0]+=1
    i=0;fs=w*h*3
    while len(raw:=rd.stdout.read(fs))==fs:
        f=np.frombuffer(raw,np.uint8).reshape(h,w,3)
        if a+i<A.debut_ia:q.wait_all();prets[i]=cv2.resize(f,(TW,TH),interpolation=cv2.INTER_LANCZOS4)
        else:q.start_async((f.astype(np.float32)/255).transpose(2,0,1)[None].copy(),i)
        i+=1;vide()
    q.wait_all();vide();wr.stdin.close();wr.wait();rd.wait();os.replace(tmp,out)
    print(f'images {a}-{a+i-1} faites, {time.time()-t0:.0f} s depuis le début',flush=True)
L=os.path.join(D,'liste.txt');open(L,'w').write(''.join(f"file 'm{a:06d}.mp4'\n" for a in range(0,N,CH)))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',L,'-c','copy',A.sortie],check=True);print('fini ->',A.sortie,f'{time.time()-t0:.0f} s')
