"""Synchronise les inscriptions de Simon et Layna depuis leur page Proprio Direct.

Une requête par courtier, user agent normal. Si la page ne répond pas ou si
aucune inscription n'est trouvée, le fichier existant est conservé.
"""
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

BASE = "https://propriodirect.com"
UA = "Mozilla/5.0 (compatible; CouillardImmobilierSync/1.0; +https://couillardimmobilier.ca)"
COURTIERS = {
    "simon": ("Simon Couillard", BASE + "/simon-couillard/"),
    "layna": ("Layna Couillard", BASE + "/layna-couillard/"),
}


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr-CA,fr;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as r:
        if r.status != 200:
            raise RuntimeError(f"HTTP {r.status}")
        return r.read().decode("utf-8", "replace")


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for c in soup.select("div.listings div.card[data-listing-id]"):
        def txt(sel):
            el = c.select_one(sel)
            return clean(el.get_text(" ")) if el else ""
        prix_txt = txt(".details .price")
        digits = re.sub(r"[^\d]", "", prix_txt)
        msg = c.select_one(".image .message")
        classes = msg.get("class", []) if msg else []
        statut = "vendu" if "sold" in classes else ("nouveau" if "new-listing" in classes else "")
        if not statut and msg and clean(msg.get_text()):
            statut = clean(msg.get_text()).lower()
        specs = [s for s in re.split(r"\|", txt(".bottom .svgs")) if s.strip()]
        img = c.select_one(".pictures img")
        photo = (img.get("src") or img.get("data-src")) if img else ""
        mls = c.get("data-listing-id")
        out.append({
            "mls": mls,
            "prix": int(digits) if digits else None,
            "adresse": txt(".details .address"),
            "ville": txt(".details .city_nbhd"),
            "type": txt(".details .type"),
            "chambres": int(specs[0]) if len(specs) > 0 and specs[0].strip().isdigit() else None,
            "sallesDeBain": int(specs[1]) if len(specs) > 1 and specs[1].strip().isdigit() else None,
            "statut": statut,
            "photo": photo or "",
            "url": BASE + c.get("data-slug-url", ""),
        })
    # Actives d'abord, vendues à la fin
    out.sort(key=lambda l: l["statut"] == "vendu")
    return out


def main():
    erreurs = 0
    for i, (cle, (nom, url)) in enumerate(COURTIERS.items()):
        if i:
            time.sleep(3)
        chemin = f"data/listings-{cle}.json"
        try:
            items = parse(fetch(url))
        except Exception as e:  # noqa: BLE001
            print(f"{cle}: échec ({e}), fichier conservé", file=sys.stderr)
            erreurs += 1
            continue
        if not items:
            print(f"{cle}: aucune inscription trouvée, fichier conservé", file=sys.stderr)
            erreurs += 1
            continue
        try:
            ancien = json.load(open(chemin, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            ancien = {}
        if ancien.get("inscriptions") == items:
            print(f"{cle}: aucun changement ({len(items)} inscriptions)")
            continue
        data = {
            "courtier": nom,
            "source": url,
            "miseAJour": datetime.now(timezone.utc).astimezone(ZoneInfo("America/Toronto")).strftime("%Y-%m-%d %H:%M"),
            "inscriptions": items,
        }
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"{cle}: {len(items)} inscriptions écrites")
    sys.exit(1 if erreurs == len(COURTIERS) else 0)


if __name__ == "__main__":
    main()
