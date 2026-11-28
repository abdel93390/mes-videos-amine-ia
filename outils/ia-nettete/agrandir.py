"""Rend une vidéo plus nette et plus grande avec l'IA Real-ESRGAN (gratuit, sur la machine).
Usage : ~/.cache/sr/env/bin/python agrandir.py <entree.mp4> <sortie.mp4> [--taille 1080x1920] [--modele general|anime] [--debut S --duree S]
- Travaille par morceaux de 1000 images dans <sortie>_morceaux/ : si la session coupe, relancer la même commande reprend où ça s'est arrêté.
- Sortie : H.264 crf 14 (intermédiaire de bonne qualité), sans son (le son vient du mixage ou de rendu.py).
- À faire sur la base vidéo AVANT rendu.py (sous-titres, badges, photos dessinés ensuite en pleine résolution, donc nets)."""
import sys,os,time,json,subprocess,threading,queue,argparse,warnings,numpy as np
warnings.filterwarnings('ignore');sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from sr import charge,agrandit
p=argparse.ArgumentParser();p.add_argument('entree');p.add_argument('sortie');p.add_argument('--taille',default='1080x1920');p.add_argument('--modele',default='general')
p.add_argument('--debut',type=float,default=0);p.add_argument('--duree',type=float,default=0);A=p.parse_args()
W,H=map(int,A.taille.split('x'))
pr=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v','-count_packets','-show_entries','stream=width,height,r_frame_rate,nb_read_packets','-of','json',A.entree],capture_output=True,text=True).stdout)['streams'][0]
w,h=pr['width'],pr['height'];num,den=map(int,pr['r_frame_rate'].split('/'));fps=num/den
a0=round(A.debut*fps);N=int(pr['nb_read_packets']) if not A.duree else round(A.duree*fps);N=min(N,int(pr['nb_read_packets'])-a0)
m=charge(A.modele);D=A.sortie+'_morceaux';os.makedirs(D,exist_ok=True);CH=1000;t0=time.time()
for a in range(a0,a0+N,CH):
    b=min(a0+N,a+CH)-1;out=os.path.join(D,f'm{a:06d}.mp4')
    if os.path.exists(out):continue
    rd=subprocess.Popen(['ffmpeg','-v','error','-i',A.entree,'-vf',f"select='between(n\\,{a}\\,{b})'",'-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    tmp=out+'.part.mp4'
    wr=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-c:v','libx264','-crf','14','-preset','veryfast','-pix_fmt','yuv420p',tmp],stdin=subprocess.PIPE)
    q=queue.Queue(8)
    def ecrit():
        while (f:=q.get()) is not None:wr.stdin.write(f)
    th=threading.Thread(target=ecrit);th.start();n=0;fs=w*h*3
    while len(raw:=rd.stdout.read(fs))==fs:
        q.put(agrandit(m,np.frombuffer(raw,np.uint8).reshape(h,w,3),(W,H)).tobytes());n+=1
    q.put(None);th.join();wr.stdin.close();wr.wait();rd.wait();os.replace(tmp,out)
    print(f"morceau {a}-{a+n-1} fait, {time.time()-t0:.0f} s depuis le début",flush=True)
L=os.path.join(D,'liste.txt');open(L,'w').write(''.join(f"file 'm{a:06d}.mp4'\n" for a in range(a0,a0+N,CH)))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',L,'-c','copy',A.sortie],check=True);print('écrit :',A.sortie)
