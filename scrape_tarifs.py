#!/usr/bin/env python3
"""
Scraper de tarifs électricité — mis à jour chaque semaine via GitHub Actions.
Sources : selectra.info et kelwatt.fr (données publiques, tarifs TTC 6 kVA).
"""

import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
}

TARIFS_FILE = "tarifs.json"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        print(f"  [ERREUR] {url} — {e}", file=sys.stderr)
        return ""


def first_float(pattern: str, text: str, default: float | None = None) -> float | None:
    m = re.search(pattern, text)
    if m:
        return float(m.group(1).replace(",", "."))
    return default


# ---------------------------------------------------------------------------
# Scrapers par fournisseur (pages Selectra / Kelwatt publiques)
# ---------------------------------------------------------------------------

def scrape_trv(html_selectra: str) -> dict | None:
    """Tarif réglementé EDF — page Selectra prix généraux."""
    base = first_float(r"tarif\s+r[eé]glement[eé][^<]{0,60}0[,\.](\d{4})\s*€", html_selectra)
    # Fallback : cherche directement le motif 0.XXXX € en option base
    base = first_float(r"option\s+[Bb]ase[^<]{0,80}(0\.\d{4})\s*€", html_selectra, base)

    hc = first_float(r"[Hh]eures\s+[Cc]reuses?\s*[:\-–]?\s*(0\.\d{4})\s*€", html_selectra)
    hp = first_float(r"[Hh]eures\s+[Pp]leines?\s*[:\-–]?\s*(0\.\d{4})\s*€", html_selectra)
    abo = first_float(r"abonnement\s+annuel\s*[:\-–]?\s*(1\d{2}\.\d{2})\s*€", html_selectra)

    if base:
        return {"kwh_base": base, "kwh_hc": hc, "kwh_hp": hp, "abo_annuel": abo}
    return None


def scrape_fournisseur(provider_id: str, html: str) -> dict:
    """Extrait base / HC / HP / abo depuis une page Kelwatt/Selectra générique."""
    result = {}

    base = first_float(r"(0\.\d{4})\s*€[^<]{0,30}[Bb]ase", html)
    if not base:
        base = first_float(r"prix\s+du\s+kWh[^<]{0,50}(0\.\d{4})\s*€", html)
    if base:
        result["kwh_base"] = base

    hc = first_float(r"[Hh]eures?\s+[Cc]reuses?[^<]{0,80}(0\.\d{4})\s*€", html)
    hp = first_float(r"[Hh]eures?\s+[Pp]leines?[^<]{0,80}(0\.\d{4})\s*€", html)
    abo = first_float(r"abonnement[^<]{0,60}(1[56789]\d\.\d{2}|2\d{2}\.\d{2})\s*€", html)

    if hc:
        result["kwh_hc"] = hc
    if hp:
        result["kwh_hp"] = hp
    if abo:
        result["abo_annuel"] = abo

    return result


# ---------------------------------------------------------------------------
# URL par fournisseur (pages publiques de comparateurs FR)
# ---------------------------------------------------------------------------

SCRAPE_TARGETS = {
    "alpiq-stable": (
        "https://www.kelwatt.fr/fournisseurs/alpiq/prix",
        "https://selectra.info/energie/fournisseurs/alpiq/tarifs",
    ),
    "ohm-extra-eco": (
        "https://www.kelwatt.fr/fournisseurs/ohm-energie/prix",
        "https://selectra.info/energie/fournisseurs/ohm-energie/tarifs",
    ),
    "ekwateur-verte-fixe": (
        "https://www.kelwatt.fr/fournisseurs/ekwateur/prix",
        "https://selectra.info/energie/fournisseurs/ekwateur/tarifs",
    ),
    "totalenergies-heures-eco": (
        "https://www.kelwatt.fr/fournisseurs/totalenergies/prix",
        "https://selectra.info/energie/fournisseurs/totalenergies/tarifs",
    ),
    "totalenergies-verte-fixe": (
        "https://www.kelwatt.fr/fournisseurs/totalenergies/prix",
        "https://selectra.info/energie/fournisseurs/totalenergies/tarifs",
    ),
    "octopus-eco-conso": (
        "https://www.kelwatt.fr/fournisseurs/octopus-energy/prix",
        "https://selectra.info/energie/fournisseurs/octopus-energy/tarifs",
    ),
    "engie-elec-ref-3ans": (
        "https://www.kelwatt.fr/fournisseurs/engie/prix",
        "https://selectra.info/energie/fournisseurs/engie/tarifs",
    ),
    "plenitude-plenifix-1an": (
        "https://www.kelwatt.fr/fournisseurs/plenitude/prix",
        "https://selectra.info/energie/fournisseurs/plenitude/tarifs",
    ),
    "edf-zen-fixe": (
        "https://www.kelwatt.fr/fournisseurs/edf/prix",
        "https://selectra.info/energie/fournisseurs/edf/tarifs",
    ),
    "edf-tarif-bleu": (
        "https://www.fournisseurs-electricite.com/contrat-electricite/prix",
        "https://selectra.info/energie/electricite/tarifs",
    ),
}

TRV_URLS = [
    "https://selectra.info/energie/electricite/tarifs",
    "https://www.lesfurets.com/energie/electricite/tarif-electricite",
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== Scraping tarifs électricité ===")

    with open(TARIFS_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # --- TRV ---
    print("\n[TRV]")
    trv_updated = False
    for url in TRV_URLS:
        print(f"  Fetch {url}")
        html = fetch(url)
        if not html:
            continue
        result = scrape_trv(html)
        if result:
            for k, v in result.items():
                if v is not None:
                    old = data["trv"].get(k)
                    data["trv"][k] = v
                    if old != v:
                        print(f"    {k}: {old} → {v}")
            trv_updated = True
            break
    if not trv_updated:
        print("  [WARN] TRV non mis à jour — valeurs précédentes conservées")

    # --- Fournisseurs ---
    updated_ids = []
    for provider in data["fournisseurs"]:
        pid = provider["id"]
        urls = SCRAPE_TARGETS.get(pid, ())
        if not urls:
            continue

        print(f"\n[{provider['nom']} — {provider['offre']}]")
        scraped = {}
        for url in urls:
            print(f"  Fetch {url}")
            html = fetch(url)
            if not html:
                continue
            partial = scrape_fournisseur(pid, html)
            scraped.update({k: v for k, v in partial.items() if v is not None})
            if "kwh_base" in scraped:
                break  # suffisant

        changed = False
        for k, v in scraped.items():
            old = provider.get(k)
            if old != v and v is not None:
                provider[k] = v
                print(f"  {k}: {old} → {v}")
                changed = True

        if not changed:
            print("  (aucun changement)")
        else:
            updated_ids.append(pid)

    # --- Timestamp ---
    data["meta"]["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if updated_ids:
        data["meta"]["last_changes"] = updated_ids

    with open(TARIFS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n=== Terminé — {len(updated_ids)} offre(s) mise(s) à jour ===")


if __name__ == "__main__":
    main()
