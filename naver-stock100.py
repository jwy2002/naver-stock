import requests
import json
import time
from bs4 import BeautifulSoup

# 네이버 시가총액 페이지에서 제공하는 27개의 모든 선택 가능 항목 식별자
all_fields = [
    "quant", "ask_buy", "amount", "market_sum", "operating_profit", 
    "per", "open_val", "ask_sell", "prev_quant", "property_total", 
    "operating_profit_increasing_rate", "roe", "high_val", "buy_total", 
    "frgn_rate", "debt_total", "net_income", "roa", "low_val", 
    "sell_total", "listed_stock_cnt", "sales", "eps", "pbr", 
    "sales_increasing_rate", "dividend", "reserve_ratio"
]

# 한 번에 요청 가능한 최대 개수인 6개 이하(안정성을 위해 5개 단위로 묶음)
chunks = [all_fields[i:i + 5] for i in range(0, len(all_fields), 5)]

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
}

# 세션을 유지해야 항목 선택(fieldIds)이 적용된 채로 시세 페이지를 가져올 수 있음
session = requests.Session()

# 종목별로 데이터를 병합할 딕셔너리 (Key: 종목코드)
merged_data = {}

print("총 27개 항목 데이터를 추출하기 위해 5개 단위로 나누어 요청을 시작합니다...")

for idx, chunk in enumerate(chunks):
    print(f"[{idx+1}/{len(chunks)}] 데이터 요청 중: {chunk}")
    
    # 1. 원하는 항목(fieldIds)을 세션 상태로 서버에 설정
    params = [('menu', 'market_sum'), ('returnUrl', 'http://finance.naver.com/sise/sise_market_sum.naver')]
    for field in chunk:
        params.append(('fieldIds', field))
        
    set_fields_res = session.get('https://finance.naver.com/sise/field_submit.naver', params=params, headers=headers)
    
    # 2. 항목이 설정된 상태로 코스피 시가총액 페이지(sosok=0) 데이터 요청
    res = session.get('https://finance.naver.com/sise/sise_market_sum.naver?sosok=0', headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find('table', {'class': 'type_2'})
    
    if table and table.find('tbody'):
        # 헤더(항목명) 추출
        thead = table.find('thead')
        headers_texts = [th.text.strip() for th in thead.find_all('th')]
        
        # 바디(종목행들) 추출
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            # 빈 줄(구분선 등) 제외
            if len(cols) < 5:
                continue
            
            try:
                # 첫 번째 컬럼: 순위, 두 번째 컬럼: 종목명/코드
                rank = cols[0].text.strip()
                a_tag = cols[1].find('a')
                if not a_tag: 
                    continue
                
                name = a_tag.text.strip()
                code = a_tag['href'].split('code=')[1] if 'code=' in a_tag['href'] else ''
                
                # 기존에 없는 종목이면 초기화
                if code not in merged_data:
                    merged_data[code] = {
                        'rank': int(rank) if rank.isdigit() else rank,
                        'code': code,
                        'name': name
                    }
                
                # 순위(0), 종목명(1) 과 맨 마지막 토론버튼을 제외한 가운데 항목들의 값 추출 추가
                for c_idx in range(2, len(cols) - 1):
                    col_name = headers_texts[c_idx]
                    col_val = cols[c_idx].text.strip().replace(',', '').replace('\t', '').replace('\n', '')
                    
                    # 현재가, 전일비, 등락률, 액면가는 매 요청마다 공통으로 존재하므로 중복 추가 방지
                    if col_name not in merged_data[code]:
                        # 숫자로 변환 가능한 경우 캐스팅 처리 시도 (퍼센트 및 각종 값 고려)
                        if col_val.replace('.', '', 1).replace('-', '', 1).isdigit() and col_val != "":
                            merged_data[code][col_name] = float(col_val) if '.' in col_val else int(col_val)
                        else:
                            merged_data[code][col_name] = col_val

            except Exception as e:
                pass
                
    # 네이버 서버 접속 거부(429 Too Many Requests 등) 방지를 위해 요청간 대기
    time.sleep(1)

# 딕셔너리를 리스트로 변환 (순위 기준으로 정렬)
final_records = list(merged_data.values())
final_records.sort(key=lambda x: x.get('rank', 9999))

# JSON 파일로 저장
with open('stock_market.json', 'w', encoding='utf-8') as f:
    json.dump(final_records, f, ensure_ascii=False, indent=4)
    
print(f"\n성공! {len(final_records)} 종목, 종목당 {len(final_records[0] if final_records else {})}개 필드를 모두 취합하여 stock_market.json 파일로 저장했습니다.")