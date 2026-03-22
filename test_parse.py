import json
from bs4 import BeautifulSoup

with open("c:/workspace/VSCodeProjects/demodev/naver-stock/stock_market.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
table = soup.find('table', {'class': 'type_2'})

records = []
if table and table.find('tbody'):
    rows = table.find('tbody').find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 13:
            continue
        
        try:
            rank = cols[0].text.strip()
            a_tag = cols[1].find('a')
            name = a_tag.text.strip()
            code = a_tag['href'].split('code=')[1] if 'code=' in a_tag['href'] else ''
            
            price = cols[2].text.strip().replace(',', '')
            change_rate = cols[4].text.strip().replace('\t', '').replace('\n', '')
            volume = cols[6].text.strip().replace(',', '')
            listed_stock_cnt = cols[7].text.strip().replace(',', '')
            market_cap = cols[8].text.strip().replace(',', '')
            foreign_ratio = cols[9].text.strip()
            per = cols[10].text.strip()
            roe = cols[11].text.strip()

            record = {
                'rank': int(rank) if rank.isdigit() else rank,
                'code': code,
                'name': name,
                'price': int(price) if price.isdigit() else price,
                'change_rate': change_rate,
                'volume': int(volume) if volume.isdigit() else volume,
                'listed_stock_cnt': int(listed_stock_cnt) if listed_stock_cnt.isdigit() else listed_stock_cnt,
                'market_cap': int(market_cap) if market_cap.isdigit() else market_cap,
                'foreign_ratio': float(foreign_ratio) if foreign_ratio.replace('.', '', 1).isdigit() else foreign_ratio,
                'per': float(per.replace(',', '')) if per.replace('.', '', 1).replace(',', '').isdigit() else per,
                'roe': float(roe.replace(',', '')) if roe.replace('.', '', 1).replace(',', '').isdigit() else roe
            }
            records.append(record)
        except Exception as e:
            print(f"Error parsing row: {e}")

print(f"Parsed {len(records)} records.")
print(records[:2])
