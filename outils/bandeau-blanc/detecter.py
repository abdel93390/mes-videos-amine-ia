"""Repère, image par image, les sous-titres d'origine écrits en blanc (ou jaune) avec un contour sombre, dans une bande horizontale.
Usage : python3 detecter.py <dossier> [--bande 0.65,0.79]   (fractions de la hauteur ; défaut : bas-milieu de l'image)
Lit <dossier>/src_origine.mp4 s'il existe, sinon src.mp4. Écrit <dossier>/st_boites.json {image: [x0,y0,x1,y1]} (coordonnées de cette vidéo)."""
import sys,os,json,argparse,numpy as np
from scipy import ndimage
sys.path.insert(0,'/home/user/amine-monteur-video-ia/amine/scripts')
from common import lire_images,probe
p=argparse.ArgumentParser();p.add_argument('d');p.add_argument('--bande',default='0.65,0.79');A=p.parse_args()
v=os.path.join(A.d,'src_origine.mp4');v=v if os.path.exists(v) else os.path.join(A.d,'src.mp4')
H=probe(v)['hauteur'];b0,b1=(float(x) for x in A.bande.split(','));Y0,Y1=int(H*b0),int(H*b1);out={}
for i,im in enumerate(lire_images(v)):
    a=im[Y0:Y1].astype(np.int16);lum=a.mean(2)
    m=((a.min(2)>=200)|((a[:,:,0]>=190)&(a[:,:,1]>=160)&(a[:,:,2]<=120)))&ndimage.binary_dilation(lum<70,iterations=2)
    rows=np.where(m.sum(1)>=4)[0]
    if m.sum()>=60 and len(rows):
        cs=np.where(m[rows.min():rows.max()+1].sum(0)>=1)[0];out[i]=[int(cs.min()),int(rows.min()+Y0),int(cs.max()),int(rows.max()+Y0)]
json.dump(out,open(os.path.join(A.d,'st_boites.json'),'w'))
hs=np.array([v[3]-v[1] for v in out.values()]) if out else np.array([0])
print(f"{len(out)} images avec sous-titre sur {i+1} ; bande {Y0}-{Y1} px ; hauteur typique {int(np.median(hs))} px ; boîtes : st_boites.json")
