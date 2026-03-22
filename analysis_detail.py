import json

# JSON 파일 경로 (SK하이닉스)
file_path = 'c:/workspace/VSCodeProjects/demodev/naver-stock/000660.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 'priceInfos' 키에 실제 일봉 데이터 목록이 들어있습니다.
price_infos = data.get('priceInfos', [])

if not price_infos:
    print("분석할 가격 데이터(일봉)가 존재하지 않습니다.")
    exit()

print(f"📊 [SK하이닉스 (000660)] 일봉 차트 데이터 분석 📊\n")
print(f"총 거래일 수: {len(price_infos)}일")
print(f"데이터 기간: {price_infos[0]['localDate']} ~ {price_infos[-1]['localDate']}\n")

# 1. 최고 종가 / 최저 종가 분석
max_close = max(price_infos, key=lambda x: x['closePrice'])
min_close = min(price_infos, key=lambda x: x['closePrice'])

print(f"📈 역대 최고 종가: {max_close['closePrice']:,}원 (달성일: {max_close['localDate']})")
print(f"📉 역대 최저 종가: {min_close['closePrice']:,}원 (기록일: {min_close['localDate']})\n")

# 2. 거래량 폭발의 날 (가장 활발하게 거래된 날)
max_volume_day = max(price_infos, key=lambda x: x['accumulatedTradingVolume'])
print(f"🔥 거래량 최대일: {max_volume_day['localDate']} (총 {max_volume_day['accumulatedTradingVolume']:,}주 거래)")
print(f"  - 당일 종가: {max_volume_day['closePrice']:,}원\n")

# 3. 외국인 보유 비중 (시작일 vs 최근일 비교)
first_fr = price_infos[0]['foreignRetentionRate']
last_fr = price_infos[-1]['foreignRetentionRate']
fr_diff = round(last_fr - first_fr, 2)

print(f"🌍 외국인 보유 비중 변화:")
print(f"  - 시작일 ({price_infos[0]['localDate']}): {first_fr}%")
print(f"  - 최근일 ({price_infos[-1]['localDate']}): {last_fr}%")
if fr_diff > 0:
    print(f"  => 외국계 자본 비중이 {fr_diff}% 증가(순매수 추세)하였사옵니다.")
else:
    print(f"  => 외국계 자본 비중이 {abs(fr_diff)}% 감소(순매도 추세)하였사옵니다.")

# 4. 가장 가격 변동폭(고가-저가)이 컸던 날 (롤러코스터 장)
max_gap_day = max(price_infos, key=lambda x: x['highPrice'] - x['lowPrice'])
gap_amt = max_gap_day['highPrice'] - max_gap_day['lowPrice']
print(f"\n🎢 일일 가격 변동폭(고가-저가) 최대일: {max_gap_day['localDate']}")
print(f"  - 변동폭: {gap_amt:,}원 (고가 {max_gap_day['highPrice']:,}원 / 저가 {max_gap_day['lowPrice']:,}원)")
