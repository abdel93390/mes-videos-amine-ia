# Cale les voix expressives : coupe le souffle avant la parole (max 0,35 s), accélère légèrement si besoin (max 1,12),
# puis enchaîne : début de parole = max(début d'origine, fin de la parole précédente + 0,06). Écrit debut dans la fiche.
import json,os,shutil,subprocess,sys
d=sys.argv[1];f=json.load(open(os.path.join(d,'fiche.json')));T=os.path.join(d,'tts');R=os.path.join(d,'tts_brut');os.makedirs(R,exist_ok=True)
PRE=0.35;VMAX=1.12
L=f['lignes']
def brut(i):
    for e in ('.mp3','.json','.cle'):
        s,b=os.path.join(T,i+e),os.path.join(R,i+e)
        if e=='.cle' and (not os.path.exists(b) or open(b).read()!=open(s).read()):
            shutil.copy(os.path.join(T,i+'.mp3'),os.path.join(R,i+'.mp3'));shutil.copy(os.path.join(T,i+'.json'),os.path.join(R,i+'.json'));shutil.copy(s,b)
    return json.load(open(os.path.join(R,i+'.json')))
ids=[l['id'] for l in L if os.path.exists(os.path.join(T,l['id']+'.v4'))]
prev=0;mx=0
for k,l in enumerate(L):
    if l['id'] not in ids:
        al=json.load(open(os.path.join(T,l['id']+'.json')));t0=al['character_start_times_seconds'][0];t1=al['character_end_times_seconds'][-1]
        fs=max(l['debut_src']-t0,prev+0.06);l['debut']=round(fs,3);prev=fs+t1;mx=max(mx,fs+t0-l['debut_src']);continue
    al=brut(l['id']);t0=al['character_start_times_seconds'][0];t1=al['character_end_times_seconds'][-1]
    cut=max(0,t0-PRE);parole=t1-t0
    nxt=L[k+1]['debut_src'] if k+1<len(L) else 336.9
    dispo=nxt-0.1-max(l['debut_src'],prev+0.06)   # temps de parole disponible avant la réplique suivante
    v=min(VMAX,max(1.0,parole/max(dispo,0.3)))
    src=os.path.join(R,l['id']+'.mp3');dst=os.path.join(T,l['id']+'.mp3')
    subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{cut:.3f}','-i',src,'-filter:a',f'atempo={v:.4f}','-c:a','libmp3lame','-b:a','160k',dst],check=True)
    n={k2:[max(0,(x-cut)/v) for x in al[k2]] for k2 in ('character_start_times_seconds','character_end_times_seconds')};n['characters']=al['characters']
    json.dump(n,open(os.path.join(T,l['id']+'.json'),'w'))
    t0n=n['character_start_times_seconds'][0];t1n=n['character_end_times_seconds'][-1]
    fs=max(l['debut_src']-t0n,prev+0.06);l['debut']=round(fs,3);prev=fs+t1n;r=fs+t0n-l['debut_src'];mx=max(mx,r)
    if r>0.3 or v>1.0:print(f"{l['id']:5s} {l['perso']:9s} vitesse {v:.2f} coupe {cut:.2f}s retard {r:.2f}s")
json.dump(f,open(os.path.join(d,'fiche.json'),'w'),ensure_ascii=False,indent=1)
print(f'retard max {mx:.2f} s ; fin de la voix {prev:.2f} s')
