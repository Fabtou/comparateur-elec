# Comparateur électricité 🐅

Site statique comparant les tarifs d'électricité des principaux fournisseurs français pour particuliers. Zéro dépendance, zéro framework, zéro cookie. Mis à jour automatiquement chaque semaine via GitHub Actions.

🔗 **[fabtou.github.io/comparateur-elec](https://Fabtou.github.io/comparateur-elec/)**

---

## Pages

| Page | Description |
|------|-------------|
| `index.html` | Comparateur de tarifs — simulation par consommation, kVA, part HC/HP |
| `calculateur-hc.html` | Calculateur de rentabilité HC/HP — seuil par fournisseur, kWh moyen pondéré |
| `conseils.html` | Conseils pratiques pour réduire sa consommation et ses dépenses |

## Structure

```
comparateur-elec/
├── index.html
├── calculateur-hc.html
├── conseils.html
├── tarifs.json                        # Source de vérité des tarifs (42 offres, 21 fournisseurs)
├── scripts/
│   └── scrape_tarifs.py               # Scraper hebdomadaire (Selectra / Kelwatt)
├── .github/workflows/
│   └── update-tarifs.yml              # GitHub Actions — chaque lundi 06h UTC
├── sitemap.xml
├── robots.txt
└── manifest.json
```

## Données

Les tarifs sont stockés dans `tarifs.json`. Chaque fournisseur y figure en double : une entrée mode `base` et une entrée mode `hc`. Le champ `meta.updated_at` est utilisé par le site pour afficher un avertissement si les données ont plus de 15 jours.

### Ajouter ou modifier un fournisseur

Éditer directement `tarifs.json`. Structure d'une offre :

```json
{
  "id": "fournisseur-offre-base",
  "fournisseur": "Nom Fournisseur",
  "offre": "Nom de l'offre",
  "mode": "base",
  "type": "fixe",
  "vert": true,
  "label_vert": "Garanties d'Origine",
  "actif": true,
  "kwh_base": 0.1673,
  "kwh_base_9kva_plus": null,
  "kwh_hc": null,
  "kwh_hp": null,
  "abo_annuel": 187.80,
  "sans_engagement": true,
  "validite": "2027-03-31",
  "url": "https://..."
}
```

Pour une offre HC/HP, dupliquer l'entrée avec `"mode": "hc"` et renseigner `kwh_hc` et `kwh_hp` (laisser `kwh_base` à `null`).

### Mise à jour manuelle

Les tarifs évoluent généralement deux fois par an (février et août). Pour mettre à jour sans attendre le scraper :

```bash
# Éditer tarifs.json, puis :
git add tarifs.json
git commit -m "chore: maj tarifs février 2026"
git push
```

## Déploiement

### GitHub Pages

```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/VOTRE_USER/comparateur-elec.git
git push -u origin main
```

Puis dans le dépôt : **Settings → Pages → Branch : main / root**

### Permissions GitHub Actions

**Settings → Actions → General → Workflow permissions → Read and write permissions**

Le workflow tourne automatiquement chaque lundi à 06h UTC. Déclenchement manuel : **Actions → Mise à jour hebdomadaire des tarifs → Run workflow**

### Alternatives (Netlify, Vercel)

Le site est un dossier de fichiers statiques — glisser-déposer sur [netlify.com/drop](https://app.netlify.com/drop) fonctionne immédiatement. Le GitHub Actions continue de mettre à jour `tarifs.json` sur le dépôt, le déploiement continu se charge du reste.

## Limites du scraper

Le scraper (`scripts/scrape_tarifs.py`) utilise des expressions régulières sur les pages HTML de Selectra et Kelwatt. Il est fragile par nature — si ces sites modifient leur structure, il cessera de fonctionner silencieusement. En cas d'échec, une issue GitHub est automatiquement créée avec un lien vers les logs.

La mise à jour manuelle de `tarifs.json` deux fois par an reste la méthode la plus fiable.

## Licence

MIT
