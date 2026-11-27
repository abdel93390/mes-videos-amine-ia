"""Remplace les mots écrits à la craie (texte polonais -> français) et l'étiquette du flacon (MyBeet -> Betalia),
image par image, sur une ou plusieurs vidéos alignées (src.mp4 et clean_vmake.mp4).
Usage : python3 craie_flacon.py <config.json> <entree1.mp4:sortie1.mp4> [<entree2.mp4:sortie2.mp4> ...]
Les masques (lettres, progression de l'écriture) sont calculés sur la première vidéo et appliqués à toutes."""
import json, subprocess, sys
import numpy as np
from scipy import ndimage as nd
from PIL import Image, ImageDraw, ImageFont

W, H = 720, 1280
CFG = json.load(open(sys.argv[1]))
PAIRES = [a.split(':') for a in sys.argv[2:]]
REF_VIDEO = PAIRES[0][0]
CRAIE_COUL = np.array([233, 236, 229], np.float32)


def lire_images(video, a, b):
    """images a..b (incluses) en uint8"""
    p = subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-vf', f"select='between(n\\,{a}\\,{b})'", '-vsync', '0',
                        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return np.frombuffer(p, np.uint8).reshape(-1, H, W, 3)


def craie(f, s=115):
    f = f.astype(np.int16)
    return (f.mean(axis=-1) > s) & ((f.max(axis=-1) - f.min(axis=-1)) < 85)


def main_bras(f):
    if f.ndim == 4:
        return np.stack([main_bras(x) for x in f])
    f = f.astype(np.int16)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    peau = (R - G > 25) & (G - B > 8) & (R - B > 45) & (R > 110)
    manche = (f.max(axis=-1) < 60) & ((f.max(axis=-1) - f.min(axis=-1)) < 9) & (np.abs(G - R) < 7)
    m = peau | manche
    lab, k = nd.label(m)
    if k:
        tailles = nd.sum(m, lab, range(1, k + 1))
        m = np.isin(lab, np.nonzero(tailles >= 600)[0] + 1)
    return nd.binary_dilation(m, iterations=5)


def poly_masque(poly, box):
    x0, y0, x1, y1 = box
    im = Image.new('L', (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(im).polygon([(x - x0, y - y0) for x, y in poly], fill=1)
    return np.array(im, bool)


# ------------------------------------------------------------------ mots à la craie
class Mot:
    def __init__(self, c):
        self.a, self.b = c['plan']
        poly = c.get('poly') or [[c['rect'][0], c['rect'][1]], [c['rect'][2], c['rect'][1]], [c['rect'][2], c['rect'][3]], [c['rect'][0], c['rect'][3]]]
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        m = 34
        self.box = (max(0, min(xs) - m), max(0, min(ys) - m), min(W, max(xs) + m), min(H, max(ys) + m))
        x0, y0, x1, y1 = self.box
        P = poly_masque(poly, self.box)
        imgs = lire_images(REF_VIDEO, self.a, self.b)[:, y0:y1, x0:x1]
        self.sc = c.get('seuil_craie', 115)
        C = craie(imgs, self.sc); Hm = main_bras(imgs)
        n = len(imgs)
        # image de référence : dans la 2e moitié du plan, la moins cachée par la main, avec le plus de craie
        cs = np.array([(C[k] & P & ~Hm[k]).sum() for k in range(n)]); hs = np.array([(Hm[k] & P).sum() for k in range(n)])
        cand = [k for k in range(n // 3, n) if cs[k] >= 0.85 * cs[n // 3:].max()]
        kref = min(cand, key=lambda k: hs[k])
        # lignes à protéger (barres, croix qui traversent le mot)
        self.bande = np.zeros(P.shape, bool)
        if c.get('proteger_lignes'):
            ext = nd.binary_dilation(P, iterations=40) & C[kref] & ~Hm[kref]
            pts = np.argwhere(ext).astype(np.float32)
            yy, xx = np.mgrid[0:P.shape[0], 0:P.shape[1]].astype(np.float32)
            trouves = []
            for deg in range(-80, 81):
                if abs(deg - c.get('angle', 0)) < 14: continue
                th = np.radians(deg)
                d = -pts[:, 1] * np.sin(th) + pts[:, 0] * np.cos(th)
                h, ed = np.histogram(d, bins=np.arange(d.min() - 2, d.max() + 4, 2))
                for i in np.nonzero(h >= c.get('seuil_ligne', 150))[0]:
                    trouves.append((int(h[i]), deg, float(ed[i] + 1)))
            trouves.sort(reverse=True); gardes = []
            extd = nd.binary_dilation(ext, iterations=1); hh_, ww_ = P.shape
            L = float(np.hypot(hh_, ww_))
            for cnt, deg, off in trouves[:400]:
                if any(abs(deg - g[1]) < 6 and abs(off - g[2]) < 10 for g in gardes): continue
                th = np.radians(deg); t = np.arange(-L, L, 2.0)
                xs_ = np.round(-off * np.sin(th) + t * np.cos(th)).astype(int); ys_ = np.round(off * np.cos(th) + t * np.sin(th)).astype(int)
                ok_ = (xs_ >= 0) & (xs_ < ww_) & (ys_ >= 0) & (ys_ < hh_)
                hit = np.zeros(len(t), bool); hit[ok_] = extd[ys_[ok_], xs_[ok_]]
                best = run = trou = 0
                for hv in hit:
                    if hv: run += 1 + trou; trou = 0
                    elif run:
                        trou += 1
                        if trou > 3: run = trou = 0
                    best = max(best, run)
                if best * 2 >= c.get('long_ligne', 110):
                    gardes.append((cnt, deg, off))
            for cnt, deg, off in gardes:
                th = np.radians(deg)
                self.bande |= np.abs(-xx * np.sin(th) + yy * np.cos(th) - off) < 4
            self.lignes_trouvees = [(g[1], round(g[2])) for g in gardes]
            self.bande &= nd.binary_dilation(P, iterations=30)
        # lettres = composantes de craie entièrement dans le polygone
        Cl = C[kref] & P & ~self.bande & ~Hm[kref]
        bord = P & ~nd.binary_erosion(P, iterations=2)
        lab, k = nd.label(Cl, structure=np.ones((3, 3)))
        touche = set(np.unique(lab[bord & (lab > 0)]))
        lettres = Cl if c.get('tout') else np.isin(lab, [i for i in range(1, k + 1) if i not in touche])
        # union sur plusieurs images complètes (une lettre cachée par la main sur l'image de référence reste détectée)
        for kk in cand[::max(1, len(cand) // 8)]:
            Ck = C[kk] & P & ~self.bande & ~Hm[kk]
            if c.get('tout'): lettres = lettres | Ck; continue
            lb, kn = nd.label(Ck, structure=np.ones((3, 3)))
            tch = set(np.unique(lb[bord & (lb > 0)]))
            lettres = lettres | np.isin(lb, [i for i in range(1, kn + 1) if i not in tch])
        self.lettres = lettres
        self.M = nd.binary_dilation(lettres, iterations=2) & ~self.bande
        if lettres.sum() < 30:
            print(f"  ! {c['texte']!r} plan {self.a}-{self.b} : lettres introuvables ({lettres.sum()} px)"); self.vide = True; return
        self.vide = False
        # progression de l'écriture
        raw = []
        for kk in range(n):
            vis = lettres & ~Hm[kk]
            raw.append((C[kk] & vis).sum() / max(vis.sum(), 1) if vis.sum() > 0.25 * lettres.sum() else np.nan)
        raw = np.array(raw)
        idx = np.arange(n); ok = ~np.isnan(raw)
        raw = np.interp(idx, idx[ok], raw[ok]) if ok.any() else np.ones(n)
        raw = nd.median_filter(raw, 5, mode='nearest')
        self.p = np.ones(n) if c.get('deja_ecrit') else np.clip((raw - 0.06) / 0.80, 0, 1)
        # bruit fixe du tableau
        g = imgs[kref].astype(np.float32)
        V = ~nd.binary_dilation(C[kref], iterations=2) & ~Hm[kref]
        hp = g - nd.gaussian_filter(g, (3, 3, 0))
        sd = float(np.std(hp[V])) if V.sum() > 50 else 3.0
        rng = np.random.default_rng(len(c['texte']) * 7919 + self.a)
        self.bruit = nd.gaussian_filter(rng.standard_normal(P.shape), 0.8) * sd * 1.6
        self.texte_calque(c, lettres)
        print(f"  {c['texte']!r:28} plan {self.a}-{self.b} lettres {int(lettres.sum())} px, angle {self.angle:+.1f}°, "
              f"lignes {getattr(self, 'lignes_trouvees', '')} écrit de l'image {self.a + int(np.argmax(self.p > 0.02))} à {self.a + int(np.argmax(self.p >= 0.999)) if (self.p >= 0.999).any() else '—'}")

    def texte_calque(self, c, lettres):
        pts = np.argwhere(lettres).astype(np.float32)  # (y, x)
        cen = pts.mean(0)
        if 'angle' in c: ang = np.radians(c['angle'])
        else:
            cov = np.cov((pts - cen).T); ev, evec = np.linalg.eigh(cov); d = evec[:, 1]
            if d[1] < 0: d = -d
            ang = np.arctan2(d[0], d[1])
            if abs(np.degrees(ang)) < 2.5: ang = 0.0
        self.angle = float(np.degrees(ang))
        ca, sa = np.cos(ang), np.sin(ang)
        u = (pts[:, 1] - cen[1]) * ca + (pts[:, 0] - cen[0]) * sa
        v = -(pts[:, 1] - cen[1]) * sa + (pts[:, 0] - cen[0]) * ca
        umin, umax = np.percentile(u, [0.5, 99.5]); vmin, vmax = np.percentile(v, [1, 99])
        lignes = c['texte'].split('\n'); nl = len(lignes)
        haut = (vmax - vmin)
        police = c.get('police', CFG['police'])
        # taille : hauteur des capitales = hauteur d'une ligne d'origine
        ref = ImageFont.truetype(police, 100); bb = ref.getbbox('H'); cap100 = bb[3] - bb[1]
        interl = c.get('interligne', 1.35)
        hl = haut / (nl + (nl - 1) * (interl - 1))
        taille = max(10, int(100 * hl * c.get('echelle', 1.0) / cap100))
        larg_max = (umax - umin) * c.get('debord', 1.12)
        while True:
            f = ImageFont.truetype(police, taille)
            lw = [f.getbbox(l)[2] - f.getbbox(l)[0] for l in lignes]
            if max(lw) <= larg_max or taille <= 10: break
            taille -= 1
        f = ImageFont.truetype(police, taille)
        capb = f.getbbox('H'); cap = capb[3] - capb[1]
        pas = cap * interl
        bloc_h = cap + pas * (nl - 1)
        bw = max(lw); cw, ch = int(bw + 40), int(bloc_h + 60)
        calque = Image.new('L', (cw, ch), 0); dr = ImageDraw.Draw(calque)
        ordre = np.zeros((ch, cw), np.float32); total = sum(lw); deja = 0
        epais = 1 if taille >= 34 else 0
        for i, l in enumerate(lignes):
            al = c.get('align', 'centre')
            x = 20 + (bw - lw[i]) * (0.5 if al == 'centre' else (1.0 if al == 'droite' else 0.0)) - f.getbbox(l)[0]
            ytop = 30 + i * pas
            dr.text((x, ytop - capb[1]), l, font=f, fill=255, stroke_width=epais, stroke_fill=255)
            y0, y1 = int(ytop - cap * 0.45), int(ytop + cap * 1.45)
            xs = np.arange(cw)
            ordre[max(0, y0):min(ch, y1), :] = np.clip((deja + (xs - x)) / total, 0, 1)[None, :]
            deja += lw[i]
        a = np.array(calque, np.float32) / 255
        rng = np.random.default_rng(42)
        tex = np.clip(0.80 + 0.22 * nd.gaussian_filter(rng.standard_normal(a.shape), 0.9) * 2.2, 0.45, 1.0)
        a = nd.gaussian_filter(a, 0.45) * tex
        # placer le calque : centre du bloc sur le centre (u, v) des lettres d'origine
        uc = (umin + umax) / 2; vc = (vmin + vmax) / 2
        hh, ww = self.M.shape
        yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        du = (xx - cen[1]) * ca + (yy - cen[0]) * sa - uc
        dv = -(xx - cen[1]) * sa + (yy - cen[0]) * ca - vc
        cx = 20 + bw / 2 + du + c.get('decalage', [0, 0])[0]; cy = 30 + bloc_h / 2 + dv + c.get('decalage', [0, 0])[1]
        self.alpha = nd.map_coordinates(a, [cy, cx], order=1, cval=0)
        self.ordre = nd.map_coordinates(ordre, [cy, cx], order=0, cval=1)

    def appliquer(self, k, img):
        """k = index dans le plan ; img = image entière (float32) modifiée sur place"""
        if self.vide: return
        p = self.p[k]
        if p <= 0.02: return
        x0, y0, x1, y1 = self.box
        reg = img[y0:y1, x0:x1]
        u8 = np.clip(reg, 0, 255)
        C = craie(u8, self.sc); Hm = main_bras(u8)
        E = self.M if p >= 0.999 else (self.M & nd.binary_dilation(C & self.M, iterations=2))
        E = E & ~Hm
        V = ~nd.binary_dilation(C, iterations=1) & ~Hm & ~self.M
        Vf = V.astype(np.float32)
        num = nd.gaussian_filter(reg * Vf[..., None], (6, 6, 0)); den = nd.gaussian_filter(Vf, 6)[..., None]
        lisse = num / np.maximum(den, 1e-3) + self.bruit[..., None]
        orig_bande = reg.copy()
        reg[E] = lisse[E]
        a = self.alpha * (self.ordre <= p) * (~Hm)
        a = a[..., None]
        reg[:] = reg * (1 - a) + CRAIE_COUL * a
        if self.bande.any():
            Bd = self.bande & nd.binary_dilation(C, iterations=1)
            reg[Bd] = orig_bande[Bd]


# ------------------------------------------------------------------ étiquette du flacon
class Etiquette:
    def __init__(self, cfg):
        e = cfg['etiquette']
        im = Image.open(e['image']).convert('RGB').crop(tuple(e['crop']))
        self.src = np.array(im, np.float32)
        self.plans = e['plans']
        # profil d'ombrage de l'étiquette Betalia (colonnes)
        self.prof_b = self._profil(self.src)

    @staticmethod
    def _rose(f):
        R, G, B = f[..., 0], f[..., 1], f[..., 2]
        return (R > 135) & (R - G > 55) & (B > 50) & (B < R)

    def _profil(self, f):
        m = self._rose(f); lum = f.mean(axis=-1)
        p = np.array([np.median(lum[:, j][m[:, j]]) if m[:, j].sum() > 3 else np.nan for j in range(f.shape[1])])
        ok = ~np.isnan(p); p = np.interp(np.arange(len(p)), np.nonzero(ok)[0], p[ok])
        p = nd.gaussian_filter1d(p, max(2, len(p) / 25))
        return p / np.percentile(p, 90)

    def rects(self, n):
        out = []
        for pl in self.plans:
            if pl['images'][0] <= n <= pl['images'][1]:
                if 'hauts' in pl:
                    top = pl['hauts'][n - pl['images'][0]]; x0, x1, h = pl['x'][0], pl['x'][1], pl['hauteur']
                    out.append([x0, top, x1, top + h])
                else:
                    out.append(pl['rect'])
        return out

    def appliquer(self, n, img):
        for (x0, y0, x1, y1) in self.rects(n):
            y0c, y1c = max(0, y0), min(H, y1)
            if y1c - y0c < 6: continue
            reg = img[y0c:y1c, x0:x1]
            rose = self._rose(reg)
            if rose.sum() < 40: continue
            zone = nd.binary_fill_holes(nd.binary_closing(rose, iterations=3))
            R, G, B = reg[..., 0], reg[..., 1], reg[..., 2]
            peau = (R - G > 25) & (G - B > 8) & (R - B > 45) & (G > 95)
            manche = (reg.max(axis=-1) < 45) & ((reg.max(axis=-1) - reg.min(axis=-1)) < 14)
            zone &= ~nd.binary_dilation(peau | manche, iterations=2)
            # étiquette Betalia à la taille du rectangle complet (y0..y1), puis rognée si le flacon sort de l'image
            hh, ww = y1 - y0, x1 - x0
            b = np.array(Image.fromarray(self.src.astype(np.uint8)).resize((ww, hh), Image.LANCZOS), np.float32)
            b = b[y0c - y0:y0c - y0 + (y1c - y0c)]
            # couleur et ombrage pris sur l'étiquette d'origine
            prof_v = self._profil(reg) if rose.sum() > 200 else np.ones(ww)
            prof_b = np.interp(np.linspace(0, 1, ww), np.linspace(0, 1, len(self.prof_b)), self.prof_b)
            ratio = np.clip(prof_v / np.maximum(prof_b, 0.2), 0.55, 1.15)
            mv = reg[rose].mean(0); rb = self._rose(b)
            mb = b[rb].mean(0) if rb.sum() > 50 else mv
            gain = np.clip(mv / np.maximum(mb, 1), 0.6, 1.5)
            b = b * gain[None, None, :] * ratio[None, :, None]
            a = nd.gaussian_filter(zone.astype(np.float32), 0.7)[..., None]
            reg[:] = reg * (1 - a) + b * a


def main():
    mots = []
    print('préparation des mots à la craie :')
    for c in CFG['mots']:
        mots.append(Mot(c))
    eti = Etiquette(CFG) if 'etiquette' in CFG else None
    for ent, sor in PAIRES:
        lect = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', ent, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        ecr = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24', '-i', '-',
                                '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-pix_fmt', 'yuv420p', sor], stdin=subprocess.PIPE)
        n = 0
        while True:
            buf = lect.stdout.read(W * H * 3)
            if len(buf) < W * H * 3: break
            actifs = [m for m in mots if m.a <= n <= m.b]
            if actifs or (eti and eti.rects(n)):
                img = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
                for m in actifs: m.appliquer(n - m.a, img)
                if eti: eti.appliquer(n, img)
                buf = np.clip(img + 0.5, 0, 255).astype(np.uint8).tobytes()
            ecr.stdin.write(buf); n += 1
        ecr.stdin.close(); ecr.wait()
        print(f'{sor} : {n} images')


main()
