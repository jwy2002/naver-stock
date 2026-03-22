import requests
from bs4 import BeautifulSoup
import time

all_fields = ["quant", "ask_buy", "amount", "market_sum", "operating_profit", "per", "open_val", "ask_sell", "prev_quant", "property_total", "operating_profit_increasing_rate", "roe", "high_val", "buy_total", "frgn_rate", "debt_total", "net_income", "roa", "low_val", "sell_total", "listed_stock_cnt", "sales", "eps", "pbr", "sales_increasing_rate", "dividend", "reserve_ratio"]

chunks = [all_fields[i:i + 5] for i in range(0, len(all_fields), 5)]
headers = {'user-agent': 'Mozilla/5.0'}

session = requests.Session()

merged_data = {}

for ch in chunks:
    # 1. 항목 설정 요청
    params = [('menu', 'market_sum'), ('returnUrl', 'http://finance.naver.com/sise/sise_market_sum.naver')]
    for field in ch:
        params.append(('fieldIds', field))
    
    res_set = session.get('https://finance.naver.com/sise/field_submit.naver', params=params, headers=headers)
    print("Setting fields:", ch, res_set.status_code)
    
    # 2. 거래소 코스피 시가총액 데이터 요청
    res = session.get('https://finance.naver.com/sise/sise_market_sum.naver?sosok=0', headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find('table', {'class': 'type_2'})
    
    if table and table.find('tbody'):
        # 헤더 추출
        thead = table.find('thead')
        headers_texts = [th.text.strip() for th in thead.find_all('th')]
        
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue
            try:
                a_tag = cols[1].find('a')
                if not a_tag: continue
                code = a_tag['href'].split('code=')[1]
                name = a_tag.text.strip()
                
                if code not in merged_data:
                    merged_data[code] = {'code': code, 'name': name, 'rank': cols[0].text.strip()}
                
                # 각 요청별 동적 컬럼 파싱 (idx 0=rank, 1=name, ... 마지막 토론버튼 이전까지)
                for idx in range(2, len(cols) - 1):
                    col_name = headers_texts[idx]
                    col_val = cols[idx].text.strip()
                    if col_name not in merged_data[code] and col_name not in ['종목명', 'N', '현재가', '전일비', '등락률', '액면가']: # 기본 컬럼 외만 취합할 경우 처리
                        merged_data[code][col_name] = col_val
                    # 현재가, 전일비, 등락률, 액면가는 항상 나옴. 중복 피하기
                    if col_name in ['현재가', '전일비', '등락률', '액면가'] and col_name not in merged_data[code]:
                        merged_data[code][col_name] = col_val

            except Exception as e:
                print("row parse err", e)
    
    time.sleep(1)

print("Parsed codes:", len(merged_data))
print(list(merged_data.items())[0])
