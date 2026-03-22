import requests
import json

# 손쉽게 가져올 종목 코드를 설정하옵니다 (예: 000660은 SK하이닉스)
stock_code = '000660'

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'origin': 'https://m.stock.naver.com',
    'priority': 'u=1, i',
    'referer': f'https://m.stock.naver.com/domestic/stock/{stock_code}/total',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36',
}

params = {
    'periodType': 'dayCandle',
}

# 대감께서 친히 발굴하신 데이터 API 주소
url = f'https://api.stock.naver.com/chart/domestic/item/{stock_code}'
response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    # 응답이 그림이 아니라 순수한 글자(JSON)이므로 바로 파이썬 딕셔너리로 엮습니다.
    data = response.json()
    
    # {종목코드}.json 파일명으로 데이터 바로 저장
    filename = f"{stock_code}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"대성공이옵니다! '{stock_code}'의 진짜 모바일 차트 데이터가 '{filename}' 문서에 고스란히 저장되었나이다.")
else:
    print(f"서버 접속 오류 발생: {response.status_code}")