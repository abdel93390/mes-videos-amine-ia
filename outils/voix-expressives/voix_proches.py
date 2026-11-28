# Trouve dans la bibliothèque ElevenLabs les voix les plus proches d'un extrait (voix isolée d'un personnage).
# Utile quand le clonage est bloqué (« detected_captcha_voice ») : la pub d'origine a souvent été faite avec ces voix-là.
# Usage : python3 voix_proches.py <extrait.mp3> [nombre]   (appel gratuit, ne consomme pas de caractères)
import json,sys,uuid,urllib.request
H={'xi-api-key':'cloud','User-Agent':'adcloner/1.0'}  # 'cloud' : le proxy de la session ajoute la vraie clé
f,n=sys.argv[1],(sys.argv[2] if len(sys.argv)>2 else '6');bd='----a'+uuid.uuid4().hex
corps=(f'--{bd}\r\nContent-Disposition: form-data; name="audio_file"; filename="x.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n').encode()+open(f,'rb').read()+(f'\r\n--{bd}\r\nContent-Disposition: form-data; name="top_k"\r\n\r\n{n}\r\n--{bd}--\r\n').encode()
r=json.load(urllib.request.urlopen(urllib.request.Request('https://api.elevenlabs.io/v1/similar-voices',corps,{**H,'Content-Type':'multipart/form-data; boundary='+bd}),timeout=120))
for v in r.get('voices',[]):print(v['voice_id'],'|',v.get('public_owner_id'),'|',v['name'],'|',v.get('language'),v.get('gender'),v.get('age'))
