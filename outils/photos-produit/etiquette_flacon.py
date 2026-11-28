"""Remplace le corps d'un petit flacon concurrent (posé sur une table, tenu en main…) par celui du flacon de l'élève, suivi image par image.
Pour un flacon trop petit ou trop court à l'écran pour remplacer tout le plan par une photo (MB1470, 28/11/2026 : flacon MyBeet sur la table, 8 s).
Usage (Python avec OpenCV, celui de l'effaceur) :
  ~/.cache/effaceur/env/bin/python etiquette_flacon.py <entree.mp4> <sortie.mp4> reglages.json [--essai 7400,7470 --apercu prefixe]
reglages.json (positions dans la vidéo d'entrée, en pixels) :
  {"photo": "travail/<REF>/produit/photo1.jpg", "photo_zone": [x0,y0,x1,y1],   corps du flacon de l'élève sur sa photo (sans le bouchon)
   "image_ref": 7470, "corps": [x0,y0,x1,y1],                                    corps du flacon concurrent sur l'image de référence
   "suivi": [x0,y0,x1,y1],                                                       modèle de suivi (flacon + bouchon, un peu plus large)
   "images": [premiere, derniere], "marge_suivi": [70,130,90]}                   plage (s'arrêter AVANT la coupe de plan) ; recherche gauche/droite, haut, bas
Ce que fait le script : suivi par corrélation (cv2.matchTemplate), couleurs du flacon de l'élève ramenées à la lumière de la scène (Lab),
même douceur que la vidéo (réduit puis agrandi), flou de bougé quand le flacon descend, doigts gardés (masque peau), bords adoucis.
Pièges : sur une image sans le flacon (avant qu'il entre, ou après la coupe), le suivi colle l'étiquette n'importe où : faire --essai sur
la première et la dernière image, et ne pas inclure l'image de la coupe. Flacon tenu en main qui tourne vite : garder plutôt la photo du plan d'avant."""
import cv2,numpy as np,subprocess,sys,json,os
E,S,RG=sys.argv[1],sys.argv[2],json.load(open(sys.argv[3]))
ESSAI=[int(x) for x in sys.argv[sys.argv.index('--essai')+1].split(',')] if '--essai' in sys.argv else None
APERCU=sys.argv[sys.argv.index('--apercu')+1] if '--apercu' in sys.argv else 'essai_flacon'
pr=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate','-of','csv=p=0',E],capture_output=True,text=True).stdout.strip().split(',')
W,H=int(pr[0]),int(pr[1]);FPS=eval(pr[2]);FS=W*H*3
A,B=RG['images'];REF=RG['image_ref'];CX0,CY0,CX1,CY1=RG['corps'];TX0,TY0,TX1,TY1=RG['suivi'];MX,MH,MB=RG.get('marge_suivi',[70,130,90])
def lire(p,ss=None,n=None):
    cmd=['ffmpeg','-v','error']+(['-ss',f'{ss/FPS+0.001:.4f}'] if ss is not None else [])+['-i',p]+(['-frames:v',str(n)] if n else [])+['-f','rawvideo','-pix_fmt','rgb24','-']
    p_=subprocess.Popen(cmd,stdout=subprocess.PIPE)
    while True:
        b=p_.stdout.read(FS)
        if len(b)<FS:break
        yield np.frombuffer(b,np.uint8).reshape(H,W,3)
ref=next(lire(E,REF,1));T=cv2.cvtColor(ref,cv2.COLOR_RGB2GRAY)[TY0:TY1,TX0:TX1]
x0p,y0p,x1p,y1p=RG['photo_zone'];ph=cv2.cvtColor(cv2.imread(RG['photo']),cv2.COLOR_BGR2RGB)[y0p:y1p,x0p:x1p]
w,h=CX1-CX0,CY1-CY0
pat=cv2.resize(cv2.resize(ph,(max(1,w//3),max(1,h//3)),interpolation=cv2.INTER_AREA),(w,h),interpolation=cv2.INTER_CUBIC)
lab=lambda x:cv2.cvtColor(x,cv2.COLOR_RGB2LAB).astype(np.float32)
o=lab(ref[CY0:CY1,CX0:CX1]);p=lab(pat)
p=(p-p.reshape(-1,3).mean(0))/(p.reshape(-1,3).std(0)+1e-3)*o.reshape(-1,3).std(0)+o.reshape(-1,3).mean(0)
pat=cv2.cvtColor(np.clip(p,0,255).astype(np.uint8),cv2.COLOR_LAB2RGB).astype(np.float32)
m=np.ones((h,w),np.float32);m[:,:2]=0;m[:,-2:]=0;m[-2:,:]=0;m=cv2.GaussianBlur(m,(5,5),1.2)
DYP=None
def poser(fr):
    global DYP
    g=cv2.cvtColor(fr,cv2.COLOR_RGB2GRAY);sx0,sy0=max(0,TX0-MX),max(0,TY0-MH)
    r=cv2.matchTemplate(g[sy0:min(H,TY1+MB),sx0:min(W,TX1+MX)],T,cv2.TM_CCOEFF_NORMED);_,sc,_,loc=cv2.minMaxLoc(r)
    dx=sx0+loc[0]-TX0;dy=sy0+loc[1]-TY0;v=0 if DYP is None else abs(dy-DYP);DYP=dy
    pp=pat if v<2 else cv2.filter2D(pat,-1,np.ones((v,1),np.float32)/v)
    x0,y0=CX0+dx,CY0+dy;zone=fr[y0:y0+h,x0:x0+w].astype(np.float32)
    hsv=cv2.cvtColor(fr[y0:y0+h,x0:x0+w],cv2.COLOR_RGB2HSV);peau=((hsv[...,0]>=4)&(hsv[...,0]<=25)&(hsv[...,1]>35)&(hsv[...,2]>50)).astype(np.float32)
    peau=cv2.GaussianBlur(cv2.dilate(peau,np.ones((3,3))),(5,5),1);mm=(m*(1-peau))[...,None]
    out=fr.copy();out[y0:y0+h,x0:x0+w]=np.clip(zone*(1-mm)+pp*mm,0,255).astype(np.uint8);return out,sc,dx,dy
if ESSAI:
    for k in ESSAI:
        fr=next(lire(E,k,1));out,sc,dx,dy=poser(fr);print(k,'score',round(sc,2),'décalage',dx,dy)
        a0,b0=max(0,CY0-120),min(H,CY1+120);c0,c1=max(0,CX0-100),min(W,CX1+100)
        cv2.imwrite(f"{APERCU}_{k}.png",cv2.cvtColor(np.hstack([fr[a0:b0,c0:c1],out[a0:b0,c0:c1]]),cv2.COLOR_RGB2BGR))
    sys.exit()
wr=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',E,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','14','-preset','veryfast','-pix_fmt','yuv420p','-c:a','copy',S],stdin=subprocess.PIPE)
sc_=[]
for i,fr in enumerate(lire(E)):
    if A<=i<=B:fr,sc,dx,dy=poser(fr);sc_.append((i,round(sc,2)))
    wr.stdin.write(np.ascontiguousarray(fr).tobytes())
wr.stdin.close();wr.wait()
print(len(sc_),'images traitées ; score de suivi le plus bas',min(s[1] for s in sc_),'; à regarder (score < 0,6) :',[s for s in sc_ if s[1]<0.6][:10])
