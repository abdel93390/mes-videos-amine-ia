"""Efface les sous-titres d'origine avec le vrai fond pris dans les images voisines (même plan), au lieu du fond lissé de Vmake.
Usage : python3 fond_temporel.py <src.mp4> <clean_vmake.mp4> <vmake_zones.json> <sortie.mp4>
Dans les rectangles de texte (vmake_zones.json), un pixel couvert par le texte prend la valeur du même pixel dans l'image
la plus proche (±K images, même plan) où il n'est ni sous un sous-titre ni sous la main ; sinon la valeur Vmake."""
import json, subprocess, sys
import numpy as np
from scipy import ndimage as nd

SRC, VM, ZONES, OUT = sys.argv[1:5]
W, H = 720, 1280
Y0, Y1 = 850, 976
K = 10 ** 4
COUPES = sorted({0, 63, 650, 1011, 1195, 1356, 1944, 2105, 2297, 3201, 3291, 3389, 3551, 3701, 3893, 3917, 4085, 4240, 4330, 4516, 4842, 4988})
FLACON = (3910, 3950, 280, 450)  # images et colonnes où le flacon glisse dans la bande : on garde Vmake
zones = {int(k): v for k, v in json.load(open(ZONES))['zones'].items()}
N = int(json.load(open(ZONES))['images_source'])


def bandes(video, a, b):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-vf', f"select='between(n\\,{a}\\,{b - 1})',crop={W}:{Y1 - Y0}:0:{Y0}", '-vsync', '0',
                        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    return np.frombuffer(p, np.uint8).reshape(-1, Y1 - Y0, W, 3)


def main_bras(f, sous=None):
    f = f.astype(np.int16); R, G, B = f[..., 0], f[..., 1], f[..., 2]
    peau = (R - G > 25) & (G - B > 8) & (R - B > 45) & (R > 110)
    moy = f.mean(-1)
    manche = (f.max(-1) < 70) & ((f.max(-1) - f.min(-1)) < 15) & (np.abs(G - R) < 12)
    if sous is not None: manche &= ~sous  # l'ombre noire d'un sous-titre n'est pas la manche
    m = peau | manche
    lab, k = nd.label(m)
    if k:
        t = nd.sum(m, lab, range(1, k + 1)); m = np.isin(lab, np.nonzero(t >= 300)[0] + 1)
    sombre = moy < 0.55 * np.median(moy)  # manche ou ombre de la main ; l'ombre d'un sous-titre reste sous 1500 px
    if sous is not None: sombre &= ~sous
    lab, k = nd.label(sombre)
    if k:
        t = nd.sum(sombre, lab, range(1, k + 1)); m |= np.isin(lab, np.nonzero(t >= 1500)[0] + 1)
    m = nd.binary_closing(nd.binary_dilation(m, iterations=5), iterations=6)  # les lettres posées sur la main restent dans la main
    return nd.binary_fill_holes(m)


def sous_titres(f):
    """masque des sous-titres d'origine : texte blanc dont l'ombre sombre est décalée de (3, 3) px ; la craie n'a pas d'ombre"""
    f = f.astype(np.int16); moy = f.mean(-1)
    blanc = (f.min(-1) > 205) & ((f.max(-1) - f.min(-1)) < 35)
    fond = nd.median_filter(moy, size=(1, 61)); sombre = moy < fond - 10
    noir = moy < 40  # ombre franche des sous-titres (la craie n'en a pas)
    ombre = np.zeros_like(noir); ombre[:-3, :-3] = noir[3:, 3:]
    sig = blanc & ombre
    lab, k = nd.label(nd.binary_dilation(blanc, iterations=3))
    if not k: return np.zeros_like(blanc)
    nb = nd.sum(blanc, lab, range(1, k + 1)); ns = nd.sum(sig, lab, range(1, k + 1))
    garde = np.nonzero((nb > 40) & (ns > 0.2 * np.maximum(nb, 1)))[0] + 1
    lettres = blanc & np.isin(lab, garde)
    m = nd.binary_dilation(lettres, iterations=3) | (sombre & nd.binary_dilation(lettres, iterations=7))
    return nd.binary_dilation(m, iterations=4)


def traiter(a, b):
    """renvoie les bandes corrigées des images a..b-1 (un morceau de plan)"""
    S = bandes(SRC, a, b); V = bandes(VM, a, b); n = len(S)
    Td = np.zeros((n, Y1 - Y0, W), bool); Sub = np.zeros_like(Td); Hm = np.zeros_like(Td); Fuite = np.zeros_like(Td); Rz = np.zeros_like(Td)
    for i in range(n):
        Sub[i] = sous_titres(S[i])
        Hm[i] = main_bras(S[i], Sub[i])
        dif = np.abs(S[i].astype(np.int16) - V[i].astype(np.int16)).max(-1) > 22
        for x0, y0, x1, y1 in zones.get(a + i, []):
            y0, y1 = max(y0, Y0) - Y0, min(y1, Y1) - Y0
            if y1 > y0: Td[i, y0:y1, x0:x1] |= dif[y0:y1, x0:x1]; Rz[i, max(0, y0 - 6):y1 + 6, max(0, x0 - 6):x1 + 6] = True
        Td[i] = nd.binary_dilation(Td[i], iterations=5) | Rz[i]  # tout le rectangle du sous-titre (ombres comprises)
        subv = sous_titres(V[i])  # sous-titre encore présent dans l'image Vmake (image mal recalée ou texte manqué)
        Fuite[i] = subv
        Sub[i] |= subv
        if FLACON[0] <= a + i <= FLACON[1]: Hm[i, :, FLACON[2]:FLACON[3]] = True
    T = Td | Sub
    # fond immobile seulement : un pixel qui change en 3 images (main qui passe, flou de mouvement) ne sert pas de modèle
    Si = S.astype(np.int16)
    stable = np.ones(T.shape, bool)
    for dk in (3, -3):
        dec = np.roll(Si, dk, axis=0)
        if dk > 0: dec[:dk] = Si[:dk]
        else: dec[dk:] = Si[dk:]
        stable &= np.abs(Si - dec).max(-1) < 14
    del Si
    valide = ~T & ~Hm & stable
    t = np.arange(n, dtype=np.int16)[:, None, None]
    der = np.maximum.accumulate(np.where(valide, t, np.int16(-30000)), axis=0)
    pro = np.minimum.accumulate(np.where(valide, t, np.int16(30000))[::-1], axis=0)[::-1]
    dd, dp = t.astype(np.int32) - der, pro.astype(np.int32) - t
    choix = np.where(dd <= dp, der, pro); dist = np.minimum(dd, dp)
    out = S.copy()
    a_ok = T & ~Hm & (dist <= K)
    ii, yy, xx = np.nonzero(a_ok)
    cand = S[choix[ii, yy, xx], yy, xx]
    # tableau attendu à cet endroit : moyenne des pixels valides voisins de la même image
    attendu = np.zeros(S.shape, np.float32)
    for i in range(n):
        ok = valide[i].astype(np.float32)
        attendu[i] = nd.gaussian_filter(S[i].astype(np.float32) * ok[..., None], (8, 8, 0)) / np.maximum(nd.gaussian_filter(ok, 8), 1e-3)[..., None]
    c16 = cand.astype(np.int16)
    dv = np.abs(c16 - V[ii, yy, xx].astype(np.int16)).max(-1).astype(np.float32)
    proche_t = np.abs(c16 - attendu[ii, yy, xx].astype(np.int16)).max(-1) < 45
    # acceptation par carrés de 8 px : le vrai fond n'est pris que s'il colle à l'image Vmake sur tout le carré
    # (écart moyen < 10, écart max < 24) ; sinon on garde Vmake, qui ne fait pas de taches sombres
    E = np.full(T.shape, np.nan, np.float32); E[ii, yy, xx] = dv
    hb, wb = T.shape[1] // 8, T.shape[2] // 8
    Eb = E[:, :hb * 8, :wb * 8].reshape(n, hb, 8, wb, 8)
    import warnings
    with np.errstate(all='ignore'), warnings.catch_warnings():
        warnings.simplefilter('ignore')
        moy_b = np.nanmean(Eb, axis=(2, 4)); max_b = np.nanmax(Eb, axis=(2, 4))
    bon = (moy_b < 10) & (max_b < 24)
    bon_px = np.zeros(T.shape, bool); bon_px[:, :hb * 8, :wb * 8] = np.repeat(np.repeat(bon, 8, 1), 8, 2)
    prend = proche_t & (bon_px[ii, yy, xx] | Fuite[ii, yy, xx])
    out[ii[prend], yy[prend], xx[prend]] = cand[prend]
    pris = np.zeros_like(T); pris[ii[prend], yy[prend], xx[prend]] = True
    # raccord d'éclairage calé sur la vraie image : pour chaque image source utilisée, écart (image courante - image source)
    # mesuré sur les pixels valides dans les deux, lissé à basse résolution
    def ecart(A, B, ok):
        h4, w4 = A.shape[0] // 4, A.shape[1] // 4
        dif = (A.astype(np.float32) - B.astype(np.float32))[:h4 * 4, :w4 * 4] * ok[:h4 * 4, :w4 * 4, None]
        okf = ok[:h4 * 4, :w4 * 4].astype(np.float32)
        ds = dif.reshape(h4, 4, w4, 4, 3).sum((1, 3)); os_ = okf.reshape(h4, 4, w4, 4).sum((1, 3))
        g = nd.gaussian_filter(ds, (3, 3, 0)) / np.maximum(nd.gaussian_filter(os_, 3), 1e-3)[..., None]
        g = np.repeat(np.repeat(g, 4, 0), 4, 1)
        full = np.zeros(A.shape, np.float32); full[:g.shape[0], :g.shape[1]] = g
        full[g.shape[0]:] = full[g.shape[0] - 1]; full[:, g.shape[1]:] = full[:, g.shape[1] - 1:g.shape[1]]
        return np.clip(nd.gaussian_filter(full, (2, 2, 0)), -25, 25)
    for i in range(n):
        if not pris[i].any(): continue
        ms, cnt = np.unique(choix[i][pris[i]], return_counts=True)
        calc = {}
        for m in ms[np.argsort(-cnt)][:6]:  # les 6 images sources les plus utilisées ; les autres prennent l'écart de la plus proche
            mut = valide[i] & valide[m]
            calc[m] = ecart(S[i], S[m], mut) if mut.sum() >= 300 else None
        for m in ms:
            mm = m if m in calc else min(calc, key=lambda q: abs(q - m))
            D = calc[mm]
            if D is None: continue
            sel = pris[i] & (choix[i] == m)
            out[i][sel] = np.clip(out[i][sel].astype(np.float32) + D[sel], 0, 255).astype(np.uint8)
    reste = T & ~pris
    for i in range(n):
        r = reste[i] & ~Fuite[i]
        if not r.any(): continue
        out[i][r] = V[i][r]  # image Vmake telle quelle (son écart moyen avec la source est d'environ 1 niveau)
    for i in range(n):  # fuite sans fond voisin : remplissage par les pixels valides de la même image
        sp = reste[i] & Fuite[i] & ~Hm[i]
        if not sp.any(): continue
        ok = (valide[i] | pris[i]).astype(np.float32); img = out[i].astype(np.float32)
        lisse = nd.gaussian_filter(img * ok[..., None], (5, 5, 0)) / np.maximum(nd.gaussian_filter(ok, 5), 1e-3)[..., None]
        out[i][sp] = np.clip(lisse[sp], 0, 255).astype(np.uint8)
    # sur la main, dans le rectangle du texte : image Vmake (recalée), comme avant ; pas de taches d'ombre
    for i in range(n):
        hz = Hm[i] & (Rz[i] | Sub[i])
        if not hz.any(): continue
        out[i][hz] = V[i][hz]
        T[i] |= hz
    # filet de sécurité : dans la bande, hors main, un pixel nettement plus sombre que l'image Vmake est une trace
    # (ombre de sous-titre ou mauvais modèle) : on prend Vmake
    for i in range(n):
        tache = ((V[i].astype(np.int16) - out[i].astype(np.int16)).mean(-1) > 22) & ~Hm[i] & ~Fuite[i]
        if tache.any():
            tache = nd.binary_dilation(tache, iterations=1) & ~Hm[i]
            out[i][tache] = V[i][tache]; T[i] |= tache
    # bords fondus entre la zone refaite et l'image d'origine
    for i in range(n):
        if not T[i].any(): continue
        al = np.clip(nd.gaussian_filter(T[i].astype(np.float32), 1.5) * 1.6, 0, 1)[..., None]
        al[T[i]] = 1.0
        out[i] = (out[i].astype(np.float32) * al + S[i].astype(np.float32) * (1 - al)).astype(np.uint8)
    return out, pris.sum() / max(T.sum(), 1)


def principal():
    lect = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    ecr = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '24', '-i', '-',
                            '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
    MORCEAU, CTX = 10 ** 6, 0
    tot = []
    for s, e in zip(COUPES[:-1], COUPES[1:]):
        for c0 in range(s, e, MORCEAU):
            c1 = min(e, c0 + MORCEAU); a, b = max(s, c0 - CTX), min(e, c1 + CTX)
            bd, part = traiter(a, b); tot.append(part)
            for k in range(c0, c1):
                fr = np.frombuffer(lect.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3).copy()
                fr[Y0:Y1] = bd[k - a]
                ecr.stdin.write(fr.tobytes())
        print(f'plan {s}-{e} fait', flush=True)
    ecr.stdin.close(); ecr.wait(); lect.kill()
    print(f'part du texte remplacée par le vrai fond : {np.mean(tot) * 100:.0f} %')


if __name__ == '__main__':
    principal()
