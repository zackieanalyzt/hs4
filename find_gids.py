import requests
import json
import re

def get_sheet_gids(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Look for sheet metadata in the HTML
            # Pattern: {"id":1732644265,"title":"2. ด้านการบริการสุขภาพ"...}
            # Or similar in bootstrap data
            content = response.text
            # Try to find all "id":NUMBER,"title":"STRING"
            matches = re.findall(r'"id":(\d+),"title":"([^"]+)"', content)
            if not matches:
                # Fallback pattern
                matches = re.findall(r'gid=(\d+)[^>]*>([^<]+)</a>', content)
            
            return {title: gid for gid, title in matches}
        else:
            print(f"Error accessing sheet: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

if __name__ == "__main__":
    sid = "1gIQbPiSMGGuNwguv55TZ0pmU9rTV8W7-Js3BcFhjVtY"
    gids = get_sheet_gids(sid)
    if gids:
        print(json.dumps(gids, ensure_ascii=False, indent=2))
    else:
        print("Could not find GIDs automatically.")
