import requests
import json
import re

def get_sheet_gids(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.text
            # Attempt to extract titles and GIDs using a different pattern
            # Look for the 'gviz' data or similar structure
            matches = re.findall(r'\{"id":(\d+),"title":"([^"]+)"', content)
            if matches:
                return {title: gid for gid, title in matches}
            
            # Another attempt: look for 'sheetId':NUMBER,'title':'STRING'
            matches = re.findall(r"'sheetId':\s*(\d+).*?'title':\s*'([^']+)'", content)
            if matches:
                return {title: gid for gid, title in matches}
                
            return {"Error": "No matches found"}
        else:
            return {"Error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"Error": str(e)}

if __name__ == "__main__":
    sid = "1gIQbPiSMGGuNwguv55TZ0pmU9rTV8W7-Js3BcFhjVtY"
    gids = get_sheet_gids(sid)
    print(json.dumps(gids, ensure_ascii=False, indent=2))
