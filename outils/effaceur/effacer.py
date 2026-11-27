"""Effaceur gratuit de sous-titres incrustés (à la place de Vmake).

Repère les sous-titres blancs à contour sombre dans leur bande, puis les efface avec LaMa
(modèle d'inpainting, licence Apache 2.0), seulement autour du texte. Tourne sur la machine, sans service payant.

Usage :
  python effacer.py <entree.mp4> <sortie.mp4> --modele big-lama.pt [--bande Y0 Y1] [--duree S]
                    [--apercu avant_apres.jpg] [--masque masque.mp4] [--largeur-max 480]
  --bande : bande des sous-titres en pixels (sinon trouvée toute seule)
  --duree : ne traiter que les S premières secondes (pour un essai rapide)
  --apercu : image avant/après de quelques moments, à regarder avant de continuer
  --masque : enregistre le masque du texte trouvé (pour vérifier le repérage)
  --largeur-max : la zone envoyée à LaMa est réduite à cette largeur au plus (vitesse) ; 0 = taille réelle
La sortie a exactement les mêmes images, la même cadence et le même son que l'entrée :
avec la méthode, l'écrire en travail/<REF>/clean_vmake.mp4 puis lancer vmake.py <dossier> --existant.
"""
import argparse, collections, json, subprocess, sys, time
import numpy as np
import cv2
import torch
from scipy import ndimage

VERSION = 'v1 (27/11/2026)'


def probe(f):
    r = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                   'stream=width,height,r_frame_rate,nb_frames:format=duration', '-of', 'json', f],
                                  capture_output=True, text=True).stdout)
    s = r['streams'][0]
    a, b = s['r_frame_rate'].split('/')
    fps = float(a) / float(b)
    n = int(s.get('nb_frames') or 0) or int(float(r['format']['duration']) * fps)
    return s['width'], s['height'], s['r_frame_rate'], fps, n


def lire(f, W, H, duree=None, vf=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', f]
    if duree:
        cmd += ['-t', str(duree)]
    if vf:
        cmd += ['-vf', vf]
    cmd += ['-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)


class Detecteur:
    """Texte blanc pur collé à un contour sombre (sous-titres classiques des pubs TikTok/Reels)."""

    def __init__(self, W, H):
        s = W / 360
        self.s = s
        self.k_sombre = np.ones((max(3, round(5 * s)),) * 2)
        self.k_ferm = np.ones((max(3, round(7 * s)), max(5, round(15 * s))))
        self.hmin, self.hmax, self.wmin = 8 * s, 80 * s, 12 * s
        self.my, self.mx = round(5 * s), round(6 * s)

    def boites(self, img, y0=0, y1=None):
        a = img[y0:y1].astype(np.int16)
        blanc = (a.min(2) > 215) & ((a.max(2) - a.min(2)) < 30)
        if not blanc.any():
            return []
        sombre = a.max(2) < 90
        t = blanc & ndimage.binary_dilation(sombre, self.k_sombre)
        if not t.any():
            return []
        t = ndimage.binary_closing(t, self.k_ferm)
        lab, _ = ndimage.label(t)
        out = []
        for sl in ndimage.find_objects(lab):
            h = sl[0].stop - sl[0].start
            w = sl[1].stop - sl[1].start
            if self.hmin < h < self.hmax and w > self.wmin:
                out.append((sl[0].start + y0, sl[0].stop + y0, sl[1].start, sl[1].stop))
        return out

    def masque(self, img, y0, y1):
        H, W = img.shape[:2]
        m = np.zeros((H, W), bool)
        for a, b, c, d in self.boites(img, y0, y1):
            m[max(0, a - self.my):b + self.my, max(0, c - self.mx):d + self.mx] = True
        return m


def trouver_bande(f, W, H, fps, det, duree):
    """Cherche la bande où les sous-titres apparaissent le plus souvent (2 images par seconde)."""
    hist = np.zeros(H)
    nb = 0
    for img in lire(f, W, H, duree, vf=f'fps=2'):
        nb += 1
        for a, b, c, d in det.boites(img):
            if (d - c) > 1.5 * (b - a):
                hist[a:b] += d - c
    if hist.max() == 0:
        return None
    lignes = hist >= 0.25 * hist.max()
    lab, _ = ndimage.label(lignes)
    pic = lab[int(hist.argmax())]
    ys = np.where(lab == pic)[0]
    # réunir les lignes voisines (sous-titres sur 2 ou 3 lignes)
    marge = round(40 * det.s)
    y0, y1 = ys.min(), ys.max() + 1
    while True:
        voisins = np.where(lignes[max(0, y0 - marge):y0])[0]
        if len(voisins) == 0:
            break
        y0 = max(0, y0 - marge) + voisins.min()
    while True:
        voisins = np.where(lignes[y1:y1 + marge])[0]
        if len(voisins) == 0:
            break
        y1 = y1 + voisins.max() + 1
    e = round(24 * det.s)
    return max(0, y0 - e), min(H, y1 + e)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('entree')
    ap.add_argument('sortie')
    ap.add_argument('--modele', required=True)
    ap.add_argument('--bande', nargs=2, type=int)
    ap.add_argument('--duree', type=float)
    ap.add_argument('--apercu')
    ap.add_argument('--masque')
    ap.add_argument('--largeur-max', type=int, default=480)
    ap.add_argument('--fils', type=int, default=0, help='threads CPU (0 = tous)')
    o = ap.parse_args()
    t0 = time.time()
    if o.fils:
        torch.set_num_threads(o.fils)
    W, H, FPS, fps, N = probe(o.entree)
    if o.duree:
        N = min(N, int(round(o.duree * fps)))
    det = Detecteur(W, H)
    print(f'effaceur {VERSION} : {W}x{H}, {N} images, {N / fps:.0f} s', flush=True)

    if o.bande:
        y0, y1 = o.bande
    else:
        b = trouver_bande(o.entree, W, H, fps, det, o.duree)
        if b is None:
            print('AUCUN sous-titre blanc à contour trouvé : cet effaceur ne sait pas traiter ce style de texte.')
            sys.exit(3)
        y0, y1 = b
    print(f'bande des sous-titres : y {y0}-{y1} (sur {H})', flush=True)

    model = torch.jit.load(o.modele, map_location='cpu').eval()
    ctx = round(40 * det.s)
    k_dil = np.ones((max(3, round(5 * det.s)),) * 2)

    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', FPS, '-i', '-']
    cmd += (['-t', str(o.duree)] if o.duree else []) + ['-i', o.entree, '-map', '0:v', '-map', '1:a?', '-c:v', 'libx264',
                                                         '-crf', '16', '-pix_fmt', 'yuv420p', '-c:a', 'copy', o.sortie]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    menc = None
    if o.masque:
        menc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'gray', '-s', f'{W}x{H}', '-r', FPS,
                                 '-i', '-', '-c:v', 'libx264', '-qp', '0', '-pix_fmt', 'yuv420p', o.masque], stdin=subprocess.PIPE)

    cibles = [int(N * k / 7) for k in range(1, 7)]
    apercus = []
    stats = {'images': 0, 'avec_texte': 0}
    t_dernier = t0

    def effacer(img, m):
        mb = ndimage.binary_dilation(m, k_dil)
        ys, xs = np.where(mb)
        a, b = max(0, ys.min() - ctx), min(H, ys.max() + 1 + ctx)
        c, d = max(0, xs.min() - ctx), min(W, xs.max() + 1 + ctx)
        crop = img[a:b, c:d]
        mm = mb[a:b, c:d]
        f = 1.0
        if o.largeur_max and (d - c) > o.largeur_max:
            f = o.largeur_max / (d - c)
        if f < 1:
            cw, ch = max(8, round((d - c) * f)), max(8, round((b - a) * f))
            x_in = cv2.resize(crop, (cw, ch), interpolation=cv2.INTER_AREA)
            m_in = cv2.resize(mm.astype(np.uint8), (cw, ch), interpolation=cv2.INTER_NEAREST) > 0
            m_in = ndimage.binary_dilation(m_in, np.ones((3, 3)))
        else:
            x_in, m_in = crop, mm
        hp, wp = ((x_in.shape[0] + 7) // 8) * 8, ((x_in.shape[1] + 7) // 8) * 8
        xp = np.pad(x_in, ((0, hp - x_in.shape[0]), (0, wp - x_in.shape[1]), (0, 0)), mode='symmetric')
        mp = np.pad(m_in, ((0, hp - m_in.shape[0]), (0, wp - m_in.shape[1])))
        x = torch.from_numpy(xp).permute(2, 0, 1)[None].float() / 255
        with torch.inference_mode():
            y = model(x, torch.from_numpy(mp).float()[None, None])
        y = (y.clamp(0, 1) * 255).byte()[0].permute(1, 2, 0).numpy()[:x_in.shape[0], :x_in.shape[1]]
        if f < 1:
            y = cv2.resize(y, (d - c, b - a), interpolation=cv2.INTER_CUBIC)
        bord = cv2.GaussianBlur(mm.astype(np.float32), (5, 5), 0)[..., None]
        new = img.copy()
        new[a:b, c:d] = (y * bord + crop * (1 - bord)).astype(np.uint8)
        return new

    def sortir(i, img, m):
        nonlocal t_dernier
        res = img
        if m.any():
            stats['avec_texte'] += 1
            res = effacer(img, m)
            if cibles and i >= cibles[0]:
                cibles.pop(0)
                apercus.append((img[y0:y1], res[y0:y1]))
        enc.stdin.write(res.tobytes())
        if menc:
            menc.stdin.write((m * 255).astype(np.uint8).tobytes())
        stats['images'] += 1
        if time.time() - t_dernier > 60:
            t_dernier = time.time()
            fait = stats['images'] / max(N, 1)
            reste = (time.time() - t0) / max(fait, 1e-3) * (1 - fait)
            print(f'  {100 * fait:.0f} % ({stats["images"]}/{N} images), encore environ {reste / 60:.0f} min', flush=True)

    # chaque image prend le masque réuni des 2 images d'avant et des 2 d'après (texte qui apparaît en fondu)
    buf = collections.deque()  # (indice, image, masque)
    lu = sorti = 0

    def sortir_suivante():
        nonlocal sorti
        base = buf[0][0]
        img = buf[sorti - base][1]
        m = np.zeros((H, W), bool)
        for j, _, mj in buf:
            if abs(j - sorti) <= 2:
                m |= mj
        sortir(sorti, img, m)
        sorti += 1
        while buf and buf[0][0] < sorti - 2:
            buf.popleft()

    for img in lire(o.entree, W, H, o.duree):
        buf.append((lu, img, det.masque(img, y0, y1)))
        lu += 1
        while sorti + 2 < lu:
            sortir_suivante()
    while sorti < lu:
        sortir_suivante()

    enc.stdin.close()
    enc.wait()
    if menc:
        menc.stdin.close()
        menc.wait()
    if o.apercu and apercus:
        lignes = []
        for avant, apres in apercus:
            sep = np.full((avant.shape[0], 6, 3), 255, np.uint8)
            lignes.append(np.hstack([avant, sep, apres]))
            lignes.append(np.full((4, lignes[-1].shape[1], 3), 255, np.uint8))
        planche = np.vstack(lignes[:-1])
        if planche.shape[1] > 1000:
            f = 1000 / planche.shape[1]
            planche = cv2.resize(planche, (1000, round(planche.shape[0] * f)), interpolation=cv2.INTER_AREA)
        cv2.imwrite(o.apercu, cv2.cvtColor(planche, cv2.COLOR_RGB2BGR))
    duree = time.time() - t0
    print(f'fini : {stats["images"]} images, texte effacé sur {stats["avec_texte"]}, en {duree / 60:.1f} min '
          f'({duree / max(stats["images"] / fps, 1e-3):.1f} fois la durée de la vidéo)')
    if stats['images'] != N:
        print(f'ATTENTION : {stats["images"]} images écrites pour {N} annoncées par la vidéo')


if __name__ == '__main__':
    main()
