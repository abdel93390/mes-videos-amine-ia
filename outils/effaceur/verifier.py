"""Vérifie le travail de l'effaceur : flou dans la zone effacée et restes de lettres.
Usage : python3 verifier.py <source.mp4> <effacee.mp4> [--bande Y0 Y1] [--max N]
- Netteté : pour chaque image où l'effaceur a changé des pixels, compare la netteté (laplacien) de la zone refaite à celle du décor juste autour.
  Rapport 1 = aussi net que le décor ; sous 0,6 = tache floue probable. Affiche la médiane et les 15 pires images (à regarder en gros plan).
- Restes : compte les pixels de texte (blanc pur collé à un contour sombre) encore présents après l'effacement, image par image.
Mesuré sur MB1470 (28/11/2026, 3D réaliste, 360x640) : rapport médian 1,05, 5 % les plus bas à 0,86, aucun reste ; les pires (0,6) invisibles à l'œil.
Travailler sur les vidéos à leur taille d'origine (avant l'agrandissement 1080) : c'est 9 fois plus rapide."""
import subprocess,sys,numpy as np,scipy.ndimage as nd
S,E=sys.argv[1],sys.argv[2]
pr=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate','-of','csv=p=0',S],capture_output=True,text=True).stdout.strip().split(',')
W,H=int(pr[0]),int(pr[1]);FPS=eval(pr[2])
Y0,Y1=(int(sys.argv[sys.argv.index('--bande')+1]),int(sys.argv[sys.argv.index('--bande')+2])) if '--bande' in sys.argv else (int(H*0.55),int(H*0.85))
MAXI=int(sys.argv[sys.argv.index('--max')+1]) if '--max' in sys.argv else 10**9
h=Y1-Y0;FS=W*h*3
def lire(p):
    q=subprocess.Popen(['ffmpeg','-v','error','-i',p,'-vf',f'crop={W}:{h}:0:{Y0}','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    while True:
        b=q.stdout.read(FS)
        if len(b)<FS:break
        yield np.frombuffer(b,np.uint8).reshape(h,W,3).astype(np.float32)
def texte(x):return (x.min(2)>225)&nd.binary_dilation(x.max(2)<70,iterations=2)
net=[];restes=[];n_txt=0
for i,(s,e) in enumerate(zip(lire(S),lire(E))):
    if i>=MAXI:break
    ts=texte(s).sum()
    if ts>40:
        n_txt+=1;te=texte(e).sum()
        if te>25 and te>0.15*ts:restes.append((i,round(i/FPS,1)))
    gs,ge=s.mean(2),e.mean(2);m=np.abs(gs-ge)>25
    if m.sum()<max(30,W*h//2000):continue
    m=nd.binary_dilation(m,iterations=2);ring=nd.binary_dilation(m,iterations=max(8,W//45))&~m
    lap=np.abs(nd.laplace(nd.gaussian_filter(ge,0.7)));net.append((i,float(lap[m].mean()/(lap[ring].mean()+1e-3))))
if net:
    r=np.array([x[1] for x in net]);print(f"netteté de la zone effacée / décor autour : médiane {np.median(r):.2f}, 5 % les plus bas {np.percentile(r,5):.2f} ({len(net)} images)")
    print("pires images (à regarder en gros plan) :",[(i,round(i/FPS,1),round(v,2)) for i,v in sorted(net,key=lambda x:x[1])[:15]])
print(f"restes de lettres : {len(restes)} image(s) sur {n_txt} avec du texte dans la source",restes[:20])
