"""Real-ESRGAN « compact » (SRVGGNetCompact, d'après github.com/xinntao/Real-ESRGAN, licence BSD-3), sur processeur.
charge(nom) -> modèle ('general' : le plus net, conseillé pour la 3D ; 'anime' : plus lisse, 2 fois plus rapide)
agrandit(modele, image_rgb_uint8, taille=(largeur, hauteur)) -> image agrandie x4 par l'IA puis ramenée à la taille voulue."""
import os,torch,torch.nn as nn,torch.nn.functional as F,numpy as np
class SRVGGNetCompact(nn.Module):
    def __init__(self,num_feat=64,num_conv=16,upscale=4):
        super().__init__();self.upscale=upscale;b=[nn.Conv2d(3,num_feat,3,1,1),nn.PReLU(num_parameters=num_feat)]
        for _ in range(num_conv):b+=[nn.Conv2d(num_feat,num_feat,3,1,1),nn.PReLU(num_parameters=num_feat)]
        b.append(nn.Conv2d(num_feat,3*upscale*upscale,3,1,1));self.body=nn.ModuleList(b);self.upsampler=nn.PixelShuffle(upscale)
    def forward(self,x):
        o=x
        for l in self.body:o=l(o)
        return self.upsampler(o)+F.interpolate(x,scale_factor=self.upscale,mode='nearest')
CONF={'anime':('animevideov3.pth',16),'general':('general-x4v3.pth',32)}
BF16=False
def charge(nom='general',dossier=os.path.expanduser('~/.cache/sr')):
    global BF16
    f,nc=CONF[nom];m=SRVGGNetCompact(num_conv=nc);sd=torch.load(os.path.join(dossier,f),map_location='cpu')
    m.load_state_dict(sd.get('params_ema',sd.get('params',sd)),strict=True);m.eval()
    BF16=any(x in open('/proc/cpuinfo').read() for x in ('amx_bf16','avx512_bf16'))  # 5 fois plus rapide, écart invisible (0,16 sur 255)
    torch.set_num_threads(os.cpu_count() or 4)
    return m.to(memory_format=torch.channels_last)
@torch.inference_mode()
def agrandit(m,im,taille=None):
    x=torch.from_numpy(np.ascontiguousarray(im)).permute(2,0,1).unsqueeze(0).float().div(255).contiguous(memory_format=torch.channels_last)
    if BF16:
        with torch.autocast('cpu',dtype=torch.bfloat16):y=m(x)
    else:y=m(x)
    y=y.float()
    if taille:y=F.interpolate(y,size=(taille[1],taille[0]),mode='bicubic',antialias=True,align_corners=False)
    return y.clamp(0,1).mul(255).round().byte()[0].permute(1,2,0).contiguous().numpy()
