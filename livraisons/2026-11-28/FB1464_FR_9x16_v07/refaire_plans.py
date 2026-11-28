"""Refait la bande des sous-titres de quelques plans avec fond_temporel.traiter et remplace ces images dans clean_vmake.mp4.
Usage : python3 refaire_plans.py a-b [a-b ...]"""
import sys, subprocess, numpy as np
plans = [tuple(map(int, p.split('-'))) for p in sys.argv[1:]]
sys.argv = ['x', 'src.mp4', 'clean_vmake_v2.mp4', 'vmake_zones.json', '/dev/null']
import fond_temporel as ft
W, H, Y0, Y1 = 720, 1280, 850, 976
neuf = {}
for a, b in plans:
    out, part = ft.traiter(a, b)
    for k in range(b - a): neuf[a + k] = out[k]
    print(f'plan {a}-{b} : {part * 100:.0f} % vrai fond', flush=True)
subprocess.run(['mv', 'clean_vmake.mp4', 'clean_vmake_avant.mp4'])
S_ = W * H * 3
lect = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', 'clean_vmake_avant.mp4', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
vm = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', 'clean_vmake_v2.mp4', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
ecr = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24', '-i', '-',
                       '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-pix_fmt', 'yuv420p', 'clean_vmake.mp4'], stdin=subprocess.PIPE)
n = 0
while True:
    x = lect.stdout.read(S_); y = vm.stdout.read(S_)
    if len(x) < S_: break
    if n in neuf or 3905 <= n <= 3955:
        C = np.frombuffer(x, np.uint8).reshape(H, W, 3).copy()
        if n in neuf: C[Y0:Y1] = neuf[n]
        if 3905 <= n <= 3955: C[Y0:Y1, 190:530] = np.frombuffer(y, np.uint8).reshape(H, W, 3)[Y0:Y1, 190:530]
        x = C.tobytes()
    ecr.stdin.write(x); n += 1
ecr.stdin.close(); ecr.wait(); print('clean_vmake.mp4', n)
