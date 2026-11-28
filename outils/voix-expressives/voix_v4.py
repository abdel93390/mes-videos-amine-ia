# Voix expressives (ElevenLabs v4 + balises d'émotion), une voix par personnage.
# Usage : python3 voix_v4.py <dossier> [L1 L2 ...] [--modele eleven_v4]
# Lit fiche.json : lignes[{id,perso,texte,ton?,debut_src,fin_fenetre}], voix.par_perso. Écrit tts/<id>.mp3 et tts/<id>.json
# (alignement limité au texte, sans la balise, pour les sous-titres). Les anciennes voix sont gardées dans tts_v2/.
import base64,hashlib,json,os,shutil,subprocess,sys,urllib.request,urllib.error
sys.path.insert(0,'/home/user/amine-monteur-video-ia/amine/scripts')
import voix as V
V.LANGUE='fr'
d=sys.argv[1];args=[a for a in sys.argv[2:] if not a.startswith('--')]
mod=sys.argv[sys.argv.index('--modele')+1] if '--modele' in sys.argv else 'eleven_v4'
if mod in args:args.remove(mod)
H={'xi-api-key':'cloud','User-Agent':'adcloner/1.0','Content-Type':'application/json'}
f=json.load(open(os.path.join(d,'fiche.json')));pp=f['voix']['par_perso']
T=os.path.join(d,'tts');B=os.path.join(d,'tts_v2')
if not os.path.exists(B):shutil.copytree(T,B)
ids=args or [l['id'] for l in f['lignes']]
def synth(voix,txt):
    c={"text":txt,"model_id":mod,"language_code":"fr"}
    for essai in range(3):
        try:return json.load(urllib.request.urlopen(urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voix}/with-timestamps?output_format=mp3_44100_128',json.dumps(c).encode(),H),timeout=180))
        except urllib.error.HTTPError as e:
            m=e.read()[:300]
            if e.code in (429,500,502,503) and essai<2:continue
            raise SystemExit(f'ElevenLabs HTTP {e.code} {m}')
tot=0;faits=[]
for l in f['lignes']:
    if l['id'] not in ids:continue
    ton=l.get('ton');txt=(f'[{ton}] ' if ton else '')+l['texte']
    cle=hashlib.md5(f"{mod}|{pp[l['perso']]}|{txt}".encode()).hexdigest()
    mp3,js,ct=[os.path.join(T,l['id']+e) for e in ('.mp3','.json','.cle')]
    if os.path.exists(ct) and open(ct).read()==cle:continue
    r=synth(pp[l['perso']],txt);tot+=len(txt)
    open(mp3,'wb').write(base64.b64decode(r['audio_base64']));al=r['alignment'];full=''.join(al['characters'])
    i=full.find(l['texte'])
    if i<0:i=full.find(l['texte'][:8])
    if i<0:i=len(full)-len(l['texte'])
    n=len(l['texte']);al={k:al[k][i:i+n] for k in ('characters','character_start_times_seconds','character_end_times_seconds')}
    json.dump(al,open(js,'w'));open(ct,'w').write(cle);open(os.path.join(T,l['id']+'.v4'),'w').write(mod);faits.append(l)
    for e in ('.ecoute.json',):
        if os.path.exists(os.path.join(T,l['id']+e)):os.remove(os.path.join(T,l['id']+e))
# réécoute groupée (Whisper) des phrases générées
res=V.ecoute_lot([(l['id'],os.path.join(T,l['id']+'.mp3'),l['texte']) for l in faits]) if faits else {}
for l in faits:
    al=json.load(open(os.path.join(T,l['id']+'.json')));e=res[l['id']]
    dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',os.path.join(T,l['id']+'.mp3')],capture_output=True,text=True).stdout)
    fen=l['fin_fenetre']-l['debut_src']
    print(f"{l['id']:5s} {l['perso']:9s} parole {al['character_start_times_seconds'][0]:4.2f}-{al['character_end_times_seconds'][-1]:4.2f}s fichier {dur:4.2f}s fenêtre {fen:5.2f}s  {'ok' if not e['ecarts'] else ('MAUVAISE ' if e['grave'] else 'à écouter ')+str(e['ecarts'][:3])}  langue {e['langue']}")
print('caractères facturés :',tot)
