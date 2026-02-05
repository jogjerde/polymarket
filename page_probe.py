import requests

base_sites = [
    "https://polymarket.com",
    "https://www.polymarket.com",
]

# sample slugs from previous probe
slugs = [
    "will-frp-win-the-second-most-seats-in-the-norway-election",
    "will-zelenskyy-wear-a-suit-before-july",
    "no-change-in-fed-interest-rates-after-july-2025-meeting",
]

for slug in slugs:
    print(f"\nChecking slug: {slug}")
    for site in base_sites:
        for path in [f"/market/{slug}", f"/markets/{slug}", f"/market/{slug}/?utm=probe"]:
            url = site + path
            try:
                resp = requests.head(url, timeout=10, allow_redirects=True)
                print(f" {url} -> {resp.status_code}")
            except Exception as e:
                print(f" {url} -> error: {e}")
