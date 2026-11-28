# Repère, image par image, la boîte des sous-titres d'origine (texte blanc à ombre portée, centré) -> <dossier>/sub_boxes.json
# Usage : python3 detecte_st.py <dossier contenant src.mp4 en 360x640> [y0,y1 de la bande, défaut 415,495]
import json,subprocess,sys,numpy as np
D=sys.argv[1];W,H=360,640;Y0,Y1=(int(v) for v in (sys.argv[2].split(',') if len(sys.argv)>2 else (415,495)))
p=subprocess.Popen(['ffmpeg','-v','error','-i',D+'/src.mp4','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
out={};k=0
while True:
    b=p.stdout.read(W*H*3)
    if len(b)<W*H*3:break
    a=np.frombuffer(b,np.uint8).reshape(H,W,3)[Y0-2:Y1+3].astype(np.int16)
    mn=a.min(2);lum=a.mean(2)
    txt=(mn[:-2,:-2]>226)&(lum[1:-1,1:-1]<lum[:-2,:-2]-55)  # pixel blanc dont le voisin bas-droite est nettement plus sombre (ombre)
    ys,xs=np.where(txt)
    if len(xs)>=12:
        cols=np.unique(xs);grp=[];cur=[cols[0],cols[0]]
        for c in cols[1:]:
            if c-cur[1]<=14:cur[1]=c
            else:grp.append(cur);cur=[c,c]
        grp.append(cur)
        g=min(grp,key=lambda g:abs((g[0]+g[1])/2-180)) if grp else None
        sel=(xs>=g[0])&(xs<=g[1])
        if sel.sum()>=12 and g[1]-g[0]>=8:
            yy=ys[sel]+Y0-2;out[k]=[int(g[0]),int(yy.min()),int(g[1])+2,int(yy.max())+2]
    k+=1
json.dump(out,open(D+'/sub_boxes.json','w'))
print(k,'images,',len(out),'avec sous-titre')
