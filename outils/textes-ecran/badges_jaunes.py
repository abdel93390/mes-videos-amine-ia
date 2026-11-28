"""Badges jaunes arrondis (« 2+1 GRATIS », « 90 DNI GWARANCJI »…) : repérés image par image (apparition animée comprise) et réécrits en français.
Usage : python3 badges_jaunes.py <dossier> <reglages.json> [--echelle 3]
reglages.json : {"images": [14669, 15060], "badges": [{"lignes_y": [505, 556], "texte": "2+1 OFFERTE"}, {"lignes_y": [556, 598], "texte": "GARANTIE 90 JOURS"}],
                 "couleur": [251, 212, 12], "texte_couleur": [26, 26, 26]}   (lignes_y : tranche de hauteur où se trouve chaque badge, coordonnées d'origine)
Lit src_origine.mp4 (ou src.mp4) ; ajoute à fiche.rendu.patches des patchs arrondis marqués "badge_jaune" (remplacés à chaque lancement), police Poppins Bold."""
import sys,os,json,argparse,numpy as np
from scipy import ndimage
sys.path.insert(0,'/home/user/amine-monteur-video-ia/amine/scripts')
from common import lire_images
p=argparse.ArgumentParser();p.add_argument('d');p.add_argument('reglages');p.add_argument('--echelle',type=float,default=1);A=p.parse_args();K=A.echelle
C=json.load(open(A.reglages));v=os.path.join(A.d,'src_origine.mp4');v=v if os.path.exists(v) else os.path.join(A.d,'src.mp4');a0,b0=C['images'];P=[]
for n,im in enumerate(lire_images(v)):
    if n<a0:continue
    if n>b0:break
    X=im.astype(int);msk=(X[:,:,0]>200)&(X[:,:,1]>165)&(X[:,:,2]<130)&(X[:,:,0]-X[:,:,2]>110);msk=ndimage.binary_closing(msk,np.ones((5,5)))
    for bd in C['badges']:
        ya,yb=bd['lignes_y'];sub=msk[ya:yb];lab,k=ndimage.label(sub)
        if k==0:continue
        sz=ndimage.sum(sub,lab,range(1,k+1));j=int(np.argmax(sz))+1
        if sz[j-1]<60:continue
        ys,xs=np.where(lab==j);x0,y0,x1,y1=int(xs.min())-2,int(ys.min()+ya)-2,int(xs.max())+3,int(ys.max()+ya)+3;h=y1-y0
        P.append({"badge_jaune":True,"images":[n,n],"rect":[round(x0*K),round(y0*K),round(x1*K),round(y1*K)],"rayon":round(h*K/2),"remplir":C.get('couleur',[251,212,12]),
                  "lignes":[{"texte":bd['texte'],"x":round((x0+x1)/2*K),"y":round(((y0+y1)/2+1)*K),"taille":round(max(8,17*h/44)*K),"graisse":700,"couleur":C.get('texte_couleur',[26,26,26]),"ancre":"mm","largeur":round((x1-x0-14)*K),"police":"Poppins-Bold.ttf"}]})
out=[]
for q in sorted(P,key=lambda q:(q['lignes'][0]['texte'],q['images'][0])):
    r=out[-1] if out else None
    if r and r['rect']==q['rect'] and r['lignes']==q['lignes'] and r['images'][1]+1==q['images'][0]:r['images'][1]=q['images'][1]
    else:out.append(q)
f=json.load(open(os.path.join(A.d,'fiche.json')));R=f.setdefault('rendu',{});R['patches']=[q for q in R.get('patches',[]) if not q.get('badge_jaune')]+out
json.dump(f,open(os.path.join(A.d,'fiche.json'),'w'),ensure_ascii=False,indent=1);print(len(out),'patchs de badges jaunes ajoutés')
