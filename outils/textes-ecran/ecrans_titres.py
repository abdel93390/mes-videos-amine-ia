"""Écran titre (texte blanc centré sur fond noir, ex. « TRZY TYGODNIE PÓŹNIEJ ») : réécrit en français.
Usage : python3 ecrans_titres.py <dossier> <reglages.json> [--echelle 3]
reglages.json : [{"images": [12205, 12260], "texte": "TROIS SEMAINES PLUS TARD", "rect": [16,296,344,338], "y": 317, "taille": 22}]
(images : plage où chercher l'écran ; seules les images vraiment noires sont traitées ; rect, y, taille en coordonnées d'origine)
Ajoute des patchs noirs marqués "ecran_titre" à fiche.rendu.patches. Penser à passer les mêmes plages à bandeau.py --sans."""
import sys,os,json,argparse,numpy as np
sys.path.insert(0,'/home/user/amine-monteur-video-ia/amine/scripts')
from common import lire_images,probe
p=argparse.ArgumentParser();p.add_argument('d');p.add_argument('reglages');p.add_argument('--echelle',type=float,default=1);A=p.parse_args();K=A.echelle
C=json.load(open(A.reglages));v=os.path.join(A.d,'src_origine.mp4');v=v if os.path.exists(v) else os.path.join(A.d,'src.mp4');W0=probe(v)['largeur'];noir={i:set() for i in range(len(C))}
fin=max(c['images'][1] for c in C)
for n,im in enumerate(lire_images(v)):
    if n>fin:break
    for i,c in enumerate(C):
        if c['images'][0]<=n<=c['images'][1] and np.median(im.mean(2))<5:noir[i].add(n)
P=[]
for i,c in enumerate(C):
    if not noir[i]:print('aucune image noire pour',c['texte']);continue
    a,b=min(noir[i]),max(noir[i]);S=lambda v:round(v*K)
    P.append({"ecran_titre":True,"images":[a,b],"rect":[S(x) for x in c['rect']],"remplir":[0,0,0],"lignes":[{"texte":c['texte'],"x":S(c.get('x',W0/2)),"y":S(c['y']),"taille":S(c.get('taille',22)),"graisse":700,"couleur":[255,255,255],"ancre":"mm","largeur":S(c['rect'][2]-c['rect'][0]-16),"police":"Poppins-Bold.ttf"}]})
    print(c['texte'],': images',a,'-',b)
f=json.load(open(os.path.join(A.d,'fiche.json')));R=f.setdefault('rendu',{});R['patches']=[q for q in R.get('patches',[]) if not q.get('ecran_titre')]+P
json.dump(f,open(os.path.join(A.d,'fiche.json'),'w'),ensure_ascii=False,indent=1)
