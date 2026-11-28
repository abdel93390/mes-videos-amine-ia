"""Prépare un dossier de rendu en 1080x1920 à partir du dossier de travail d'une petite source (ex. 360x640).
Usage : python3 passer_en_1080.py travail/<REF> travail/<REF>_1080 [--taille 1080x1920]
- analyse.json : largeur/hauteur à la nouvelle taille ; fiche.json : positions et tailles de rendu.patches et rendu.textes multipliées par l'échelle ;
- liens vers tts/, dm/, produit/ ; copie de mix.wav, cues_final.json, inserts.json s'ils existent.
Reste à mettre la base vidéo agrandie en <dossier 1080>/src.mp4 (outils/ia-nettete/agrandir.py, puis photos produit), puis rendu.py,
puis cp cues_final.json cues.json et controle.py. Le crf de la fiche est mis à 20 : c'est la seule compression (pas de recompression derrière)."""
import sys,os,json,shutil,argparse
p=argparse.ArgumentParser();p.add_argument('src');p.add_argument('dst');p.add_argument('--taille',default='1080x1920');A=p.parse_args()
W,H=map(int,A.taille.split('x'));os.makedirs(A.dst,exist_ok=True)
an=json.load(open(os.path.join(A.src,'analyse.json')));K=W/an['largeur'];an['largeur'],an['hauteur']=W,H
json.dump(an,open(os.path.join(A.dst,'analyse.json'),'w'),ensure_ascii=False)
f=json.load(open(os.path.join(A.src,'fiche.json')));R=f.get('rendu',{})
def sc(d,cles):
    for k in cles:
        if k in d:d[k]=[round(v*K) for v in d[k]] if isinstance(d[k],list) else round(d[k]*K)
for pt in R.get('patches',[]):
    sc(pt,('rect','rayon'))
    for l in pt.get('lignes',[]):sc(l,('x','y','taille','largeur'))
for t in R.get('textes',[]):sc(t,('y','x','taille','largeur','decalage','trait'))
if 'sous_titres' in R:sc(R['sous_titres'],('y','taille','largeur','decalage','trait'))
R['crf']=20;json.dump(f,open(os.path.join(A.dst,'fiche.json'),'w'),ensure_ascii=False,indent=1)
for n in ('tts','dm','produit'):
    s=os.path.abspath(os.path.join(A.src,n));t=os.path.join(A.dst,n)
    if os.path.exists(s) and not os.path.exists(t):os.symlink(s,t)
for n in ('mix.wav','cues_final.json','inserts.json'):
    if os.path.exists(os.path.join(A.src,n)):shutil.copy(os.path.join(A.src,n),A.dst)
print(f"dossier {A.dst} prêt (échelle {K:g}) ; reste : src.mp4 agrandi, rendu.py, cues.json, controle.py")
