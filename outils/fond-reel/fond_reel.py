# Efface des sous-titres incrustés (texte blanc à ombre portée) avec le VRAI fond : chaque carré caché par le texte est repris
# dans l'image la plus proche du même plan où il est visible (si le voisinage colle, donc fond immobile) ; LaMa (Apache 2.0)
# seulement pour le reste, calculé à mi-résolution puis agrandi.
# Usage : python3 fond_reel.py <source.mp4> <sortie.mp4> <première image> <dernière image> --boites sub_boxes.json --analyse analyse.json [--echelle 2]
#   --boites : {image: [x0,y0,x1,y1]} mesurées sur une version 360x640 de la même vidéo (detecte_st.py) ; --echelle 2 pour une source 720x1280.
#   Modèle LaMa : variable LAMA_MODELE (défaut ~/.cache/lama/big-lama.pt, voir LISEZMOI.md).
import json,os,subprocess,sys,time
import numpy as np,torch
from scipy import ndimage
from PIL import Image
import argparse
P=argparse.ArgumentParser();P.add_argument('src');P.add_argument('out');P.add_argument('k0',type=int);P.add_argument('k1',type=int)
P.add_argument('--boites',required=True);P.add_argument('--analyse',required=True);P.add_argument('--echelle',type=int,default=1)
P.add_argument('--bande',default='405,500',help='bande des sous-titres en coordonnées 360x640');A=P.parse_args()
S=A.echelle;W,H=360*S,640*S;Y0,Y1=[int(v)*S for v in A.bande.split(',')];C=6*S;K=150;SEUIL=9.0
torch.set_num_threads(4)
lama=torch.jit.load(os.environ.get('LAMA_MODELE',os.path.expanduser('~/.cache/lama/big-lama.pt')),map_location='cpu').eval()
B={int(k):[v*S for v in b] for k,b in json.load(open(A.boites)).items()}
an=json.load(open(A.analyse));cut=sorted(set(an['plans']+[an['images']]))

def masque(a,bx):
    """lettres blanches + leur ombre portée (décalée de 2 px en 360, donc 4 px ici), un peu élargies"""
    x0,y0,x1,y1=bx;x0,y0,x1,y1=max(x0-6*S,0),max(y0-5*S,0),min(x1+6*S,W),min(y1+6*S,H);d=2*S
    z=a[y0:y1+d,x0:x1+d].astype(np.float32);mn=z.min(2);lum=z.mean(2)
    bord=(mn[:-d,:-d]>185)&(lum[d:,d:]<lum[:-d,:-d]-40)
    blanc=(mn[:-d,:-d]>200)&ndimage.binary_dilation(bord,iterations=2*S)
    sombre=(lum[:-d,:-d]<ndimage.uniform_filter(lum,9*S)[:-d,:-d]-12)&ndimage.binary_dilation(blanc,iterations=4*S)
    m=np.zeros((H,W),bool);m[y0:y1,x0:x1]=ndimage.binary_dilation(blanc|bord|sombre,iterations=3*S);return m

def lama_demi(a,m):
    """LaMa sur une copie à mi-résolution de la zone, résultat agrandi et posé seulement dans le masque"""
    ys,xs=np.where(m)
    if len(ys)==0:return a
    c=48*S;y0,y1,x0,x1=max(ys.min()-c,0),min(ys.max()+c+1,H),max(xs.min()-c,0),min(xs.max()+c+1,W)
    h,w=y1-y0,x1-x0;hs,ws=h//S,w//S
    img=np.array(Image.fromarray(a[y0:y1,x0:x1]).resize((ws,hs),Image.BICUBIC));mk=np.array(Image.fromarray(m[y0:y1,x0:x1].astype(np.uint8)*255).resize((ws,hs),Image.BILINEAR))>40
    ph,pw=(-hs)%8,(-ws)%8;img=np.pad(img,((0,ph),(0,pw),(0,0)),mode='reflect').astype(np.float32)/255;mkp=np.pad(mk,((0,ph),(0,pw))).astype(np.float32)
    with torch.no_grad():out=lama(torch.from_numpy(img).permute(2,0,1)[None],torch.from_numpy(mkp)[None,None])[0].permute(1,2,0).numpy()[:hs,:ws]*255
    out=np.array(Image.fromarray(np.clip(out,0,255).astype(np.uint8)).resize((w,h),Image.BICUBIC)).astype(np.float32)
    al=ndimage.gaussian_filter(m[y0:y1,x0:x1].astype(np.float32),0.8*S)[...,None];al=np.maximum(al,m[y0:y1,x0:x1][...,None])
    r=a.copy();r[y0:y1,x0:x1]=np.clip(a[y0:y1,x0:x1]*(1-al)+out*al,0,255).astype(np.uint8);return r

def plan(k):
    i=np.searchsorted(cut,k,side='right');return cut[i-1],cut[i]
def lire(src,a,b):
    p=subprocess.run(['ffmpeg','-v','error','-i',src,'-vf',f'select=between(n\\,{a}\\,{b-1})','-vsync','0','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    return np.frombuffer(p,np.uint8).reshape(-1,H,W,3)

if __name__=='__main__':
    src,out,k0,k1=A.src,A.out,A.k0,A.k1
    ecr=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-crf','12','-preset','medium','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    t0=time.time();k=k0;st=[0,0]
    while k<=k1:
        a,b=plan(k);b=min(b,k1+1);F=lire(src,a,b);n=len(F)
        M=np.zeros((n,H,W),bool)
        for i in range(n):
            if a+i in B:M[i]=masque(F[i],B[a+i])
        gy,gx=(Y1-Y0)//C,W//C
        Mb=M[:,Y0:Y0+gy*C,:gx*C].reshape(n,gy,C,gx,C)
        occ=ndimage.binary_dilation(Mb.any(axis=(2,4)),structure=np.ones((1,3,3),bool))
        Fb=F[:,Y0:Y0+gy*C,:gx*C].astype(np.float32)
        for i in range(n):
            if a+i<k:continue
            if not M[i].any():ecr.stdin.write(F[i].tobytes());continue
            r=F[i].astype(np.float32);reste=M[i].copy()
            for cy,cx in zip(*np.nonzero(Mb[i].any(axis=(1,3)))):
                ya,yb,xa,xb=cy*C,cy*C+C,cx*C,cx*C+C
                ry0,ry1,rx0,rx1=max(0,ya-5*S),min(gy*C,yb+5*S),max(0,xa-5*S),min(gx*C,xb+5*S)
                for d in range(1,K):
                    for j in (i-d,i+d):
                        if j<0 or j>=n or occ[j,cy,cx]:continue
                        lib=~M[i,Y0+ry0:Y0+ry1,rx0:rx1]&~M[j,Y0+ry0:Y0+ry1,rx0:rx1]
                        if lib.sum()<12*S*S:continue
                        ri,rj=Fb[i,ry0:ry1,rx0:rx1][lib],Fb[j,ry0:ry1,rx0:rx1][lib]
                        if np.abs(ri-rj).mean()>SEUIL:continue
                        m=M[i,Y0+ya:Y0+yb,xa:xb]
                        r[Y0+ya:Y0+yb,xa:xb][m]=Fb[j,ya:yb,xa:xb][m]+(ri.mean(0)-rj.mean(0));reste[Y0+ya:Y0+yb,xa:xb][m]=False;st[0]+=1;break
                    else:continue
                    break
                else:st[1]+=1
            r=np.clip(r,0,255).astype(np.uint8)
            if reste.any():r=lama_demi(r,ndimage.binary_dilation(reste,iterations=S)&M[i])
            ecr.stdin.write(r.tobytes())
        k=b
        print(f'{k} / {k1}  vrai fond {st[0]}  LaMa {st[1]}  {time.time()-t0:.0f}s',flush=True)
    ecr.stdin.close();ecr.wait();print('fini ->',out)
