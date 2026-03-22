from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import time
import os

app = Flask(__name__, static_folder='.')
CORS(app) # 브라우저의 CORS 제약을 모두 허용 (로컬 개발 환경)

# --- [1] 시가총액 Top 50 실시간 스크래핑 (naver-stock100.py 로직 계승) ---
@app.route('/api/market')
def get_market_data():
    all_fields = [
        "quant", "ask_buy", "amount", "market_sum", "operating_profit",
        "per", "open_val", "ask_sell", "prev_quant", "property_total",
        "operating_profit_increasing_rate", "roe", "high_val", "buy_total", "frgn_rate",
        "debt_total", "net_income", "roa", "low_val", "sell_total",
        "listed_stock_cnt", "sales", "eps", "pbr", "sales_increasing_rate",
        "dividend", "reserve_ratio"
    ]
    # 빠르고 안정적으로 가져오기 위해 15개 단위 청크로 늘려 요청 횟수를 2번으로 단축
    chunks = [all_fields[i:i + 15] for i in range(0, len(all_fields), 15)]
    session = requests.Session()
    merged_data = {}
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    }
    
    for chunk in chunks:
        params = [('menu', 'market_sum'), ('returnUrl', 'http://finance.naver.com/sise/sise_market_sum.naver')]
        for field in chunk:
            params.append(('fieldIds', field))
            
        session.get('https://finance.naver.com/sise/field_submit.naver', params=params, headers=headers)
        res = session.get('https://finance.naver.com/sise/sise_market_sum.naver?sosok=0', headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table', {'class': 'type_2'})
        
        if table and table.find('tbody'):
            thead = table.find('thead')
            headers_texts = [th.text.strip() for th in thead.find_all('th')]
            rows = table.find('tbody').find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 5:
                    continue
                try:
                    rank = cols[0].text.strip()
                    a_tag = cols[1].find('a')
                    if not a_tag: continue
                    
                    name = a_tag.text.strip()
                    code = a_tag['href'].split('code=')[1] if 'code=' in a_tag['href'] else ''
                    
                    if code not in merged_data:
                        merged_data[code] = {
                            'rank': int(rank) if rank.isdigit() else rank,
                            'code': code,
                            'name': name
                        }
                    
                    for c_idx in range(2, len(cols) - 1):
                        col_name = headers_texts[c_idx]
                        col_val = cols[c_idx].text.strip().replace(',','').replace('\t','').replace('\n','')
                        if col_name not in merged_data[code]:
                            if col_val.replace('.', '', 1).replace('-', '', 1).isdigit() and col_val != "":
                                merged_data[code][col_name] = float(col_val) if '.' in col_val else int(col_val)
                            else:
                                merged_data[code][col_name] = col_val
                except Exception:
                    pass
        time.sleep(0.3)
        
    final_records = list(merged_data.values())
    final_records.sort(key=lambda x: x.get('rank', 9999))
    return jsonify(final_records)

# --- [2] 모바일 API 일봉 데이터 실시간 통신 (stock_detail.py 로직 계승) ---
@app.route('/api/detail/<code>')
def get_stock_detail(code):
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://m.stock.naver.com',
        'referer': f'https://m.stock.naver.com/domestic/stock/{code}/total',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
    }
    params = {'periodType': 'dayCandle'}
    url = f'https://api.stock.naver.com/chart/domestic/item/{code}'
    
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": f"Failed to fetch data from Naver. Status: {response.status_code}"}), response.status_code

# --- [3] 메인 대시보드(HTML) 서빙 ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    print("==================================================================")
    print("여봐라! 실시간 주식 대시보드 서버(Flask)가 힘차게 가동을 시작하였노라!")
    print("브라우저를 열고 http://127.0.0.1:5000 으로 당장 접속해 보시옵소서!")
    print("==================================================================")
    app.run(host='0.0.0.0', port=5000, debug=False)
