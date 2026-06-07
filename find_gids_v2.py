import requests
import json
import re

def get_sheet_gids(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.text
            # Use a more generic pattern to find the sheet data in the JS objects
            # Google Sheets often stores this in a JSON-like structure within the HTML
            matches = re.findall(r'\[(\d+),"([^"]+)",', content)
            
            results = {}
            for gid, title in matches:
                if len(gid) > 3: # GIDs are usually long, except for the first one (0)
                    results[title] = gid
                elif gid == '0':
                    results[title] = gid
            return results
        else:
            return None
    except Exception as e:
        return None

if __name__ == "__main__":
    sid = "1gIQbPiSMGGuNwguv55TZ0pmU9rTV8W7-Js3BcFhjVtY"
    gids = get_sheet_gids(sid)
    print(json.dumps(gids, ensure_ascii=False, indent=2))
