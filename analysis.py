import json

with open('c:/workspace/VSCodeProjects/demodev/naver-stock/stock_market.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"총 종목 수: {len(data)}")

if len(data) == 0:
    exit()

def get_valid_values(key, reverse=True):
    valid = [d for d in data if d.get(key) != "N/A" and isinstance(d.get(key), (int, float))]
    return sorted(valid, key=lambda x: x[key], reverse=reverse)

print("\n--- 시가총액 Top 5 (단위: 억 원) ---")
for d in get_valid_values('시가총액')[:5]:
    print(f"{d['rank']}위 {d['name']}: {d['시가총액']:,}")

print("\n--- 영업이익 Top 5 (단위: 억 원) ---")
for d in get_valid_values('영업이익')[:5]:
    print(f"{d['rank']}위 {d['name']}: {d['영업이익']:,}")

print("\n--- ROE (자기자본이익률) Top 5 (%) ---")
for d in get_valid_values('ROE')[:5]:
    print(f"{d['rank']}위 {d['name']}: {d['ROE']}%")

print("\n--- PER (주가수익비율) 저평가 Top 5 (배) ---")
for d in get_valid_values('PER', reverse=False)[:5]: # PER은 낮을수록 저평가
    print(f"{d['rank']}위 {d['name']}: {d['PER']}")

print("\n--- 외국인비율 Top 5 (%) ---")
for d in get_valid_values('외국인비율')[:5]:
    print(f"{d['rank']}위 {d['name']}: {d['외국인비율']}%")

print("\n--- 배당금 Top 5 (원) ---")
for d in get_valid_values('보통주배당금')[:5]:
    print(f"{d['rank']}위 {d['name']}: {d['보통주배당금']:,}")

# N/A 결측치 분석
na_counts = {}
for d in data:
    for k, v in d.items():
        if v == "N/A":
            na_counts[k] = na_counts.get(k, 0) + 1

if na_counts:
    print("\n--- 재무 데이터가 없는(N/A) 항목 현황 ---")
    for k, v in sorted(na_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{k}: {v}개 종목 누락")
