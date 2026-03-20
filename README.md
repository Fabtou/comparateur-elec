# ⚡ Comparateur Électricité France

Site statique monopage qui compare les tarifs d'électricité des principaux fournisseurs français, avec mise à jour automatique chaque semaine via GitHub Actions.

## Structure du projet

```
comparateur-elec/
├── index.html              # Page principale (HTML/CSS/JS pur, zéro dépendance)
├── tarifs.json             # Tarifs TTC — mis à jour automatiquement
├── scripts/
│   └── scrape_tarifs.py    # Script Python de scraping (lancé par GitHub Actions)
├── .github/
│   └── workflows/
│       └── update-tarifs.yml  # Workflow GitHub Actions (chaque lundi 06h UTC)
└── README.md
```

## Déploiement en 5 minutes

### 1. Créer le dépôt GitHub

```bash
git init
git add .
git commit -m "init: comparateur électricité"
git branch -M main
git remote add origin https://github.com/VOTRE_USER/comparateur-elec.git
git push -u origin main
```

### 2. Activer GitHub Pages

Dans votre dépôt GitHub :  
**Settings → Pages → Source : Deploy from a branch → Branch : main / root**

Votre site sera disponible sur `https://VOTRE_USER.github.io/comparateur-elec/`

### 3. Vérifier les permissions GitHub Actions

**Settings → Actions → General → Workflow permissions**  
→ Cochez **"Read and write permissions"**

Le workflow tourne automatiquement chaque lundi à 06h00 UTC.  
Vous pouvez aussi le déclencher manuellement : **Actions → Mise à jour hebdomadaire des tarifs → Run workflow**

---

## Mise à jour manuelle des tarifs

Si vous souhaitez mettre à jour `tarifs.json` sans attendre le scraper :

```bash
python3 scripts/scrape_tarifs.py
git add tarifs.json
git commit -m "chore: maj tarifs manuelle"
git push
```

## Ajouter un fournisseur

Ajoutez une entrée dans `tarifs.json` :

```json
{
  "id": "mint-energie-online-green",
  "nom": "Mint Énergie",
  "offre": "Online & Green",
  "type": "indexe",
  "vert": true,
  "vert_option": false,
  "label_vert": "Garanties d'Origine",
  "kwh_base": 0.1767,
  "kwh_hc": 0.1490,
  "kwh_hp": 0.1990,
  "abo_annuel": 187.80,
  "sans_engagement": true,
  "url": "https://www.mint-energie.com"
}
```

Puis ajoutez l'URL de scraping dans `scripts/scrape_tarifs.py` dans le dictionnaire `SCRAPE_TARGETS`.

## Déploiement alternatif : Netlify / Vercel

**Netlify** : glissez le dossier sur [app.netlify.com/drop](https://app.netlify.com/drop)  
**Vercel** : `npx vercel` dans le dossier

Pour le scraping automatique sur Netlify/Vercel, le GitHub Actions reste la solution recommandée (il push vers GitHub, le déploiement continu se charge du reste).

## Limites du scraper

Le scraper est basé sur des expressions régulières appliquées sur les pages HTML de Selectra et Kelwatt. Si ces sites modifient leur structure HTML, le scraper peut cesser de fonctionner. Dans ce cas :

1. Vérifiez les logs GitHub Actions
2. Mettez à jour les patterns dans `scrape_tarifs.py`
3. Ou mettez à jour `tarifs.json` manuellement

Les tarifs évoluent généralement **deux fois par an** (1er février et 1er août).

## Licence

MIT — libre d'utilisation et de modification.
