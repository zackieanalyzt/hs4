import requests
import json
import re

def get_sheet_gids(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.text
            # Use a very broad pattern to find anything that looks like a gid/title pair
            # [1732644265,"2. ด้านการบริการสุขภาพ",0,0,0,0,null,null,null,0,0,null,null,null,0]
            matches = re.findall(r'\[(\d{5,15}),"([^"]+)",', content)
            
            results = {title: gid for gid, title in matches}
            # Special case for the first sheet (gid=0)
            if '0' not in results.values():
                 m0 = re.search(r'\[0,"([^"]+)",', content)
                 if m0:
                     results[m0.group(1)] = "0"
            
            return results
        else:
            return {"Error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"Error": str(e)}

if __name__ == "__main__":
    sid = "1gIQbPiSMGGuNwguv55TZ0pmU9rTV8W7-Js3BcFhjVtY"
    gids = get_sheet_gids(sid)
    print(json.dumps(gids, ensure_ascii=False, indent=2))
