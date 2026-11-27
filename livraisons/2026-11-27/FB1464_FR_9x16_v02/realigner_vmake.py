"""Réaligne une sortie Vmake qui a perdu des images en cours de route (dérive) sur la source, image par image.
Usage : python3 realigner_vmake.py <src.mp4> <vmake_original.mp4> <sortie.mp4>"""
import subprocess,sys,json,numpy as np
src,vm,out=sys.argv[1:4]
def petit(f):
    r=subprocess.run(['ffmpeg','-v','error','-i',f,'-vf','scale=72:128,format=gray','-f','rawvideo','-'],capture_output=True).stdout
    return np.frombuffer(r,np.uint8).reshape(-1,128,72).astype(np.float32)
S=petit(src);V=petit(vm);nS,nV=len(S),len(V);r=nV/nS
m=[];prev=0
for j in range(nS):
    est=min(nV-1,round(j*r));lo=max(prev,est-5);hi=min(nV,est+6)
    if lo>=hi:lo=hi-1
    e=[((S[j]-V[i])**2).mean()+0.5*abs(i-est) for i in range(lo,hi)]
    i=lo+int(np.argmin(e));m.append(i);prev=i
dup=sum(1 for a,b in zip(m,m[1:]) if a==b);saut=sum(1 for a,b in zip(m,m[1:]) if b>a+1)
print(f"source {nS} images, vmake {nV} : {dup} images répétées, {saut} sauts")
json.dump(m,open(out+'.correspondance.json','w'))
W,H=map(int,subprocess.run(['ffprobe','-v','error','-select_streams','v','-show_entries','stream=width,height','-of','csv=p=0',vm],capture_output=True,text=True).stdout.strip().split(','))
fps=subprocess.run(['ffprobe','-v','error','-select_streams','v','-show_entries','stream=r_frame_rate','-of','csv=p=0',src],capture_output=True,text=True).stdout.strip()
lect=subprocess.Popen(['ffmpeg','-v','error','-i',vm,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
ecr=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',fps,'-i','-','-c:v','libx264','-crf','12','-preset','fast','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
n=W*H*3;cur=-1;buf=None
for i in m:
    while cur<i:
        buf=lect.stdout.read(n);cur+=1
    ecr.stdin.write(buf)
ecr.stdin.close();ecr.wait();lect.kill()
print('écrit',out)
