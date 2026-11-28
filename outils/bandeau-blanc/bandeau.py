"""Bandeau blanc (0 crédit, à la place de Vmake) : cache les sous-titres d'origine et écrit la traduction en noir dedans.
Usage : python3 bandeau.py <dossier> [--traduction traduction.json] [--echelle 3] [--sans a-b,c-d] [--taille 19]
Sources des sous-titres français :
  - par défaut : la voix finale (fiche.lignes + tts/<id>.json, après voix.py et enchainer.py) ;
  - --traduction <fichier> : test gratuit sans voix française, liste [["i-j" (numéros de mots de analyse.json) | "tA-B" (secondes), "texte"], ...] ;
    « | » dans un texte force une coupure de sous-titre.
Lit st_boites.json (detecter.py, coordonnées de la vidéo d'origine), fiche.rendu.remplacements (plans remplacés : boîte de l'image donneuse)
et inserts.json s'il existe ([[a,b],...] : images sans sous-titre d'origine, ex. photos produit).
Écrit dans fiche.rendu.patches les patchs du bandeau (marqués "bandeau": true, remplacés à chaque lancement ; les autres patchs sont gardés)
et cues_final.json (sous-titres en images), à copier en cues.json APRÈS rendu.py (rendu.py l'écrase) pour controle.py.
--echelle : facteur entre la vidéo d'origine et la vidéo rendue (3 pour 360x640 -> 1080x1920). --sans : images où le bandeau ne s'affiche jamais (écrans titres)."""
import sys,os,json,re,argparse,numpy as np
sys.path.insert(0,'/home/user/amine-monteur-video-ia/amine/scripts')
from common import police,carte_remplacements
p=argparse.ArgumentParser();p.add_argument('d');p.add_argument('--traduction');p.add_argument('--echelle',type=float,default=1);p.add_argument('--sans',default='')
p.add_argument('--taille',type=int,default=19);A=p.parse_args();d=A.d
f=json.load(open(os.path.join(d,'fiche.json')));an=json.load(open(os.path.join(d,'analyse.json')));fps=an['fps'];N=an['images'];K=A.echelle
bx={int(k):v for k,v in json.load(open(os.path.join(d,'st_boites.json'))).items()}
W0=int(round(an['largeur']/K));H0=int(round(an['hauteur']/K))
# géométrie du bandeau (coordonnées d'origine) : boîte typique d'une ligne et de deux lignes
ys0=np.array([v[1] for v in bx.values()]);ys1=np.array([v[3] for v in bx.values()]);h1=int(np.median(ys1-ys0));yc=int(np.median((ys0+ys1)/2))
X0,X1=max(4,int(np.percentile([v[0] for v in bx.values()],5))-10),min(W0-4,int(np.percentile([v[2] for v in bx.values()],95))+10)
X0=min(X0,W0-X1);X1=W0-X0  # centré
Y1L=(yc-h1//2-8,yc+h1//2+9);Y2L=(yc-h1-11,yc+h1+11);LH=round(A.taille*1.16)
T=A.taille;F=police(T,700);LARG=X1-X0-24;w=lambda s:F.getlength(s)
PETITS=set("le la les un une des de du d' mon ma mes ton ta tes son sa ses ce cet cette ces et ou à au aux en dans sur par pour avec sans que qui ne comme si s'il est a n' j' l' qu' s' on pas plus".split())
def lignes(txt,n):
    ws=txt.split();best=None
    def rec(k,start,acc):
        nonlocal best
        if k==1:
            parts=acc+[' '.join(ws[start:])]
            if any(w(x)>LARG for x in parts):return
            L=[w(x) for x in parts];sc=max(L)-min(L) if len(L)>1 else 0
            for x in parts[:-1]:
                last=x.split()[-1].lower()
                if re.search(r"[,.:;!?»…]$",last):sc-=160
                if last in PETITS:sc+=120
            if best is None or sc<best[0]:best=(sc,parts)
            return
        for e in range(start+1,len(ws)-k+2):rec(k-1,e,acc+[' '.join(ws[start:e])])
    rec(n,0,[]);return best[1] if best else None
def morceaux(txt,dur):
    n=1
    while lignes(txt,n) is None:n+=1
    L=lignes(txt,n);per=2 if (n>1 and dur/n<1.0) else 1;return [L[k:k+per] for k in range(0,len(L),per)]
cues=[]
if A.traduction:
    M=an['mots']
    for spec,txt in json.load(open(A.traduction)):
        if spec.startswith('t'):a,b=map(float,spec[1:].split('-'))
        else:i,j=map(int,spec.split('-'));a,b=M[i]['a'],M[j]['b']
        parts=[x.strip() for x in txt.split(' | ')];tot=sum(len(x) for x in parts);t=a
        for x in parts:
            dd=(b-a)*len(x)/tot;gs=morceaux(x,dd);tg=sum(len(' '.join(g)) for g in gs);u=t
            for g in gs:e=dd*len(' '.join(g))/tg;cues.append([u,u+e,g]);u+=e
            t+=dd
else:
    for l in f['lignes']:
        al=json.load(open(os.path.join(d,'tts',l['id']+'.json')));full=''.join(al['characters']);st=al['character_start_times_seconds'];en=al['character_end_times_seconds'];pos=0
        for g in morceaux(l['texte'].strip(),en[-1]):
            ptxt=' '.join(g);j=full.index(ptxt.split()[0],pos);fin=j+len(ptxt);pos=fin
            cues.append([l['debut']+st[j],l['debut']+en[min(fin,len(en))-1]+0.12,g])
cues.sort(key=lambda c:c[0])
for a,b in zip(cues[:-1],cues[1:]):
    if a[1]>b[0]-0.03 or b[0]-a[1]<0.7:a[1]=b[0]-0.03
cues[-1][1]=min(cues[-1][1]+0.4,N/fps-0.02)
cf=[[round(a*fps),max(round(a*fps)+12,round(b*fps)),g] for a,b,g in cues]
for q,r in zip(cf[:-1],cf[1:]):q[1]=min(q[1],r[0])
txtf=[None]*N
for a,b,g in cf:
    for o in range(max(0,a),min(N,b)):txtf[o]=tuple(g)
carte,_=carte_remplacements(f.get('rendu',{}))
INS=json.load(open(os.path.join(d,'inserts.json'))) if os.path.exists(os.path.join(d,'inserts.json')) else []
SANS=set()
for r in [x for x in A.sans.split(',') if x]:
    a,b=map(int,r.split('-'));SANS|=set(range(a,b+1))
src=lambda o:carte.get(o,o)
pres=[(src(o) in bx) and not any(a<=o<=b for a,b in INS) for o in range(N)]
deux=[pres[o] and bx[src(o)][1]<=Y2L[0]+14 and bx[src(o)][3]>=Y2L[1]-14 for o in range(N)]
def runs(v):
    r=[];s=None
    for o,x in enumerate(list(v)+[False]):
        if x and s is None:s=o
        if not x and s is not None:r.append([s,o-1]);s=None
    return r
d2=[False]*N
for s,e in runs(deux):
    if e-s+1>=5:
        for o in range(max(0,s-3),min(N,e+4)):d2[o]=True
vis=[pres[o] or txtf[o] is not None for o in range(N)];m=[]
for s,e in runs(vis):
    if m and s-m[-1][1]<=16:m[-1][1]=e
    else:m.append([s,e])
vis=[False]*N
for s,e in m:
    for o in range(s,e+1):vis[o]=True
etat=[None]*N;prev=None;nxt=[None]*N;cur=None
for o in range(N-1,-1,-1):
    if txtf[o] is not None:cur=txtf[o]
    nxt[o]=cur
for o in range(N):
    t=txtf[o]
    if t is None:t=prev if prev else nxt[o]
    else:prev=t
    if vis[o] and t and o not in SANS:etat[o]=(t,d2[o] or len(t)>1)
P=[];s=None;S=lambda v:round(v*K)
for o in range(N+1):
    e=etat[o] if o<N else None
    if s is not None and e!=etat[s]:
        (t,tall)=etat[s];y0,y1=Y2L if tall else Y1L;ys=[yc] if len(t)==1 else [yc-LH/2,yc+LH/2]
        P.append({"bandeau":True,"images":[s,o-1],"rect":[S(X0),S(y0),S(X1),S(y1)],"remplir":[255,255,255],"lignes":[{"texte":x,"x":S(W0/2),"y":S(y),"taille":S(T),"graisse":700,"couleur":[0,0,0],"ancre":"mm","largeur":S(LARG)} for x,y in zip(t,ys)]})
        s=None
    if e is not None and s is None:s=o
R=f.setdefault('rendu',{});R['patches']=[q for q in R.get('patches',[]) if not q.get('bandeau')]+P
json.dump(f,open(os.path.join(d,'fiche.json'),'w'),ensure_ascii=False,indent=1)
json.dump([[a,b,' '.join(g)] for a,b,g in cf],open(os.path.join(d,'cues_final.json'),'w'),ensure_ascii=False)
print(f"{len(cf)} sous-titres, {len(P)} patchs de bandeau ; bandeau x {X0}-{X1}, 1 ligne y {Y1L}, 2 lignes y {Y2L} (coordonnées d'origine, échelle {K})")
print('plus courts :',sorted([(round((b-a)/fps,2),' / '.join(g)) for a,b,g in cf])[:4])
