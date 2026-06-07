import requests
import csv
import json
import io
import os
from datetime import datetime

def fetch_sheet_data(sheet_id, gid):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return list(csv.reader(io.StringIO(response.text)))
        else:
            print(f"Error fetching GID {gid}: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching GID {gid}: {e}")
        return None

def process_google_sheets():
    sheet_id = "1gIQbPiSMGGuNwguv55TZ0pmU9rTV8W7-Js3BcFhjVtY"
    
    target_configs = [
        {"name": "ด้านที่ 1 การบริหารจัดการ", "gid": "224848204"},
        {"name": "ด้านที่ 2 การบริการสุขภาพ", "gid": "436568485"},
        {"name": "ด้านที่ 3 อาคาร สถานที่และสิ่งอำนวยความสะดวก", "gid": "1095125870"},
        {"name": "ด้านที่ 4 สิ่งแวดล้อม", "gid": "463522191"},
        {"name": "ด้านที่ 5 ความปลอดภัย", "gid": "802347761"},
        {"name": "ด้านที่ 6 เครื่องมืออุปกรณ์ทางการแพทย์", "gid": "2043104987"},
        {"name": "ด้านที่ 7 ระบบสนับสนุนบริการที่สำคัญ", "gid": "1017580441"},
        {"name": "ด้านที่ 8 สุขศึกษาและพฤติกรรมสุขภาพ", "gid": "1902948812"},
        {"name": "ด้านที่ 9 การรักษาความมั่นคงปลอดภัยไซเบอร์", "gid": "1389107320"}
    ]
    
    dashboard_data = []

    for config in target_configs:
        rows = fetch_sheet_data(sheet_id, config['gid'])
        if not rows: continue
        
        status_counts = {'ไม่ต้องแก้ไข': 0, 'ยังไม่ได้แก้ไข': 0, 'แก้ไขแล้ว': 0, 'ไม่แก้ไข ยืนยันเดิม': 0}
        col_idx, advice_col_idx = 5, 4
        is_pending = config['name'] in ["ด้านที่ 3 อาคาร สถานที่และสิ่งอำนวยความสะดวก", "ด้านที่ 4 สิ่งแวดล้อม", "ด้านที่ 9 การรักษาความมั่นคงปลอดภัยไซเบอร์"]

        for idx, row in enumerate(rows[:35]):
            if row and len(row) > 0 and 'ข้อที่' in str(row[0]):
                for i, cell in enumerate(row):
                    if cell and 'การแก้ไข' in str(cell): col_idx = i
                    if cell and 'คำแนะนำ' in str(cell): advice_col_idx = i
                
                for d_row in rows[idx+1:]:
                    if not d_row or not d_row[0] or not any(char.isdigit() for char in str(d_row[0])): continue
                    status = d_row[col_idx] if len(d_row) > col_idx else None
                    advice = d_row[advice_col_idx] if len(d_row) > advice_col_idx else None
                    if status in ['ยังไม่ได้แก้ไข', 'แก้ไขแล้ว', 'ไม่แก้ไข ยืนยันเดิม']: status_counts[status] += 1
                    elif advice == 'N/A' or (not status and not is_pending): status_counts['ไม่ต้องแก้ไข'] += 1
                break
        
        total_items = sum(status_counts.values())
        dashboard_data.append({
            "aspect": config['name'],
            "gid": config['gid'],
            "status_counts": status_counts,
            "is_pending": is_pending and total_items == 0,
            "has_data": total_items > 0
        })

    return {"aspects": dashboard_data, "sheet_id": sheet_id}

def generate_html(data):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html_template = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HS4 Progress Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Sarabun', sans-serif; background-color: #f1f5f9; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; color: #0f172a; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        @media (max-width: 1100px) { .grid { grid-template-columns: repeat(2, 1fr); } }
        @media (max-width: 750px) { .grid { grid-template-columns: 1fr; } }
        .card { background: #fff; border-radius: 12px; padding: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); height: 380px; border: 1px solid #e2e8f0; transition: transform 0.2s; position: relative; }
        .card:hover { transform: translateY(-3px); border-color: #2563eb; cursor: pointer; }
        .card-title { font-weight: 700; font-size: 15px; text-align: center; margin-bottom: 10px; height: 45px; display: flex; align-items: center; justify-content: center; border-bottom: 1px solid #f1f5f9; }
        .pie-container { flex-grow: 1; width: 100%; height: 280px; }
        .no-data { display: flex; align-items: center; justify-content: center; height: 280px; color: #94a3b8; font-style: italic; text-align: center; width: 100%; }
        .footer { text-align: center; margin-top: 30px; font-size: 12px; color: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ความก้าวหน้ามาตรฐาน HS4 (คลิกที่การ์ดเพื่อเปิดชีต)</h1>
        <div class="grid" id="charts-grid"></div>
        <div class="footer">
            <p>อัปเดตล่าสุด: UPDATE_TIME_PLACEHOLDER</p>
            <p>แหล่งข้อมูล: Google Sheets (Cloud)</p>
        </div>
    </div>
    <script>
        const rawData = DATA_PLACEHOLDER;
        const sheetId = rawData.sheet_id;
        const grid = document.getElementById('charts-grid');

        function openGoogleSheet(gid) {
            window.open(`https://docs.google.com/spreadsheets/d/${sheetId}/edit#gid=${gid}`, '_blank');
        }

        rawData.aspects.forEach((item, idx) => {
            const card = document.createElement('div');
            card.className = 'card';
            card.onclick = () => openGoogleSheet(item.gid);
            
            const title = document.createElement('div');
            title.className = 'card-title';
            title.innerText = item.aspect;
            card.appendChild(title);
            
            const total = Object.values(item.status_counts).reduce((a, b) => a + b, 0);
            
            if (item.is_pending) {
                const noData = document.createElement('div');
                noData.className = 'no-data';
                noData.innerText = '⚠️ รอการประเมินจากกรรมการ';
                card.appendChild(noData);
            } else if (item.has_data) {
                const chartDiv = document.createElement('div');
                chartDiv.id = `pie-${idx}`;
                chartDiv.className = 'pie-container';
                card.appendChild(chartDiv);
            } else {
                const noData = document.createElement('div');
                noData.className = 'no-data';
                noData.innerText = 'ไม่มีข้อมูลการประเมิน';
                card.appendChild(noData);
            }
            
            grid.appendChild(card);

            if (!item.is_pending && item.has_data) {
                const chart = echarts.init(document.getElementById(`pie-${idx}`));
                chart.setOption({
                    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
                    legend: { bottom: '0', left: 'center', textStyle: { fontSize: 10 }, itemWidth: 8, itemHeight: 8 },
                    series: [{
                        type: 'pie', radius: ['40%', '65%'], center: ['50%', '45%'],
                        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
                        label: { show: true, position: 'outside', formatter: '{d}%', fontSize: 11 },
                        data: [
                            { value: item.status_counts['ไม่ต้องแก้ไข'], name: 'ผ่านเกณฑ์', itemStyle: {color: '#10b981'} },
                            { value: item.status_counts['ยังไม่ได้แก้ไข'], name: 'ยังไม่ได้แก้ไข', itemStyle: {color: '#ef4444'} },
                            { value: item.status_counts['แก้ไขแล้ว'], name: 'แก้ไขแล้ว', itemStyle: {color: '#3b82f6'} },
                            { value: item.status_counts['ไม่แก้ไข ยืนยันเดิม'], name: 'ไม่แก้ไข ยืนยันเดิม', itemStyle: {color: '#f59e0b'} }
                        ]
                    }]
                });
            }
        });

        window.addEventListener('resize', () => {
            rawData.aspects.forEach((_, i) => {
                const chart = echarts.getInstanceByDom(document.getElementById(`pie-${i}`));
                if (chart) chart.resize();
            });
        });
    </script>
</body>
</html>
"""
    json_data = json.dumps(data, ensure_ascii=False)
    final_html = html_template.replace('DATA_PLACEHOLDER', json_data)
    final_html = final_html.replace('UPDATE_TIME_PLACEHOLDER', now)
    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"Fixed Dashboard generated: dashboard.html (at {now})")

if __name__ == "__main__":
    data = process_google_sheets()
    generate_html(data)
