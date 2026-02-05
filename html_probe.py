import requests
import re
import json

# Sample market slug from trades
slug = "no-change-in-fed-interest-rates-after-july-2025-meeting"
url = f"https://polymarket.com/market/{slug}"

print(f"Fetching {url}...")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

resp = requests.get(url, headers=headers, timeout=10)
print(f"Status: {resp.status_code}\n")

if resp.status_code == 200:
    text = resp.text
    
    # Extract all JSON-LD and embedded data
    # Look for window.__INITIAL_STATE__ or similar
    
    # Pattern 1: Look for "resolved" field
    resolved_match = re.search(r'"resolved"\s*:\s*(true|false)', text, re.IGNORECASE)
    if resolved_match:
        print(f"Found resolved: {resolved_match.group(1)}")
    
    # Pattern 2: Look for market status text
    if '"closed"' in text:
        closed_match = re.search(r'"closed"\s*:\s*(true|false)', text)
        if closed_match:
            print(f"Found closed: {closed_match.group(1)}")
    
    # Pattern 3: Look for "marketStatus" or similar
    status_match = re.search(r'"(?:market)?[Ss]tatus"\s*:\s*"([^"]+)"', text)
    if status_match:
        print(f"Found status: {status_match.group(1)}")
    
    # Pattern 4: Look for outcome/winner text
    if 'winner' in text.lower():
        print("Page contains 'winner' (market likely resolved)")
    elif 'open' in text.lower() and 'trading' in text.lower():
        print("Page indicates trading is open")
    
    # Extract larger JSON blocks that might contain market data
    json_blocks = re.findall(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', text, re.DOTALL)
    if json_blocks:
        print(f"\nFound window.__INITIAL_STATE__ block")
        try:
            # Just show structure, not full content
            data = json.loads(json_blocks[0][:500])  # First 500 chars
            print("(Partial structure available)")
        except:
            print("(Could not parse)")
    
    # Look for any large JSON object
    large_json = re.findall(r'\{["\'](?:market|data|state)["\'][^}]*\}', text)
    if large_json:
        print(f"\nFound {len(large_json)} potential market data objects")
