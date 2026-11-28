# Journal des photos produit

## v1 — 27-28/11/2026 (MYBEET → Betalia, velyzio.com)
- Flacon MyBeet (14126-14668, 8 min) remplacé par les photos Betalia : img1 (flacon sur fond rose) recadrée avec zoom lent, img4 (« Soutien de la circulation ») entière sur fond flou, badge « 2+1 OFFERTE ».
- Plans « verser les gélules » (12142-12210) : aller-retour sur les images de la main sans flacon.
- Recadrages : cx 0,285 évite la colonne d'icônes à droite de img1 ; zoom 1,22 → 1,14 coupait « BETTERAVE » : 1,22 au plus avec cx 0,31.
- La fiche du produit a changé le script : Betalia n'est pas « pressé à froid » mais « obtenu à basse température » (photo comparative img3), 1100 mg par jour.
- Le CDN Shopify a répondu « local_rate_limited » une fois : nouvel essai après quelques secondes (dans recuperer.py).
- Outils rangés ici le 28/11.

## Étiquette du petit flacon suivie image par image (28/11/2026, MB1470, pub MyBeet → Betalia)
Flacon MyBeet posé sur une table de 4:05 à 4:13 pendant que le narrateur parle (étiquette illisible mais présente). `etiquette_flacon.py` : corps du flacon Betalia (photo1) posé sur le flacon d'origine, suivi par `cv2.matchTemplate` (score 0,93 à 0,98 une fois posé, 0,6 à 0,8 pendant que la main le pose), couleurs ramenées à la lumière de la pièce, flou de bougé, doigts gardés. Résultat jugé naturel (lumière et douceur raccord).
Pièges vus : avant que le flacon soit dans la zone de recherche (tenu en main plus haut), le suivi collait l'étiquette sur le canapé ; et la dernière image de la plage était déjà la coupe du plan suivant (étiquette collée sur la cheminée). Solutions : photo du plan précédent prolongée de 0,7 s sur les images « en main », plage arrêtée 1 image avant la coupe.
