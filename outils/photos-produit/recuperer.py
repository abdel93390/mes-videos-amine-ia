"""Récupère la fiche produit Shopify de l'élève (textes, prix, variantes) et ses photos.
Usage : python3 recuperer.py <lien du produit> <dossier>   → <dossier>/produit.json, img1.png, img2.png… et une planche apercu.jpg"""
import sys,os,json,time,re,html,urllib.request
from PIL import Image
lien,d=sys.argv[1].split('?')[0].rstrip('/'),sys.argv[2];os.makedirs(d,exist_ok=True)
def get(u,essais=4):
    for k in range(essais):
        try:return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read()
        except Exception as e:
            if k==essais-1:raise
            time.sleep(3*(k+1))  # le CDN Shopify limite parfois (« local_rate_limited »)
p=json.loads(get(lien+'.json'))['product'];json.dump(p,open(os.path.join(d,'produit.json'),'w'),ensure_ascii=False,indent=1)
print(p['title'],'|',p.get('vendor'));[print(' variante :',v['title'],v['price']) for v in p.get('variants',[])]
print(' description :',html.unescape(re.sub(r'\s+',' ',re.sub('<[^>]+>',' ',p.get('body_html') or '')))[:600])
ims=[]
for i,im in enumerate(p.get('images',[]),1):
    f=os.path.join(d,f'img{i}.png');open(f,'wb').write(get(im['src']));ims.append(Image.open(f).convert('RGB').resize((300,300)));time.sleep(1)
if ims:
    sh=Image.new('RGB',(900,300*((len(ims)+2)//3)),(255,255,255))
    for k,im in enumerate(ims):sh.paste(im,((k%3)*300,(k//3)*300))
    sh.save(os.path.join(d,'apercu.jpg'),quality=85);print(len(ims),'photos ; planche :',os.path.join(d,'apercu.jpg'))
