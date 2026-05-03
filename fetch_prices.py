import os, json, time, requests
from datetime import date

FINNHUB_KEY = os.environ["FINNHUB_KEY"]

STOCKS = [
  # AI / 빅테크
  ("ai1","MSFT"), ("ai2","GOOGL"), ("ai3","META"), ("ai4","AMZN"), ("ai5","AAPL"),
  # 반도체
  ("sc1","NVDA"), ("sc2","SOXL"), ("sc3","INTC"), ("sc4","MU"), ("sc5","AVGO"),
  ("sc6","ASML"), ("sc7","TSM"), ("sc8","QCOM"),
  # 데이터센터 / 전력
  ("dc1","VRT"), ("dc2","EQIX"), ("dc3","GEV"), ("dc4","ETN"), ("dc5","DLR"),
  # 에너지 / 원전
  ("en1","CEG"), ("en2","CCJ"), ("en3","OKLO"), ("en4","LEU"), ("en5","UEC"), ("en6","AR"),
  # 우주
  ("sp1","RKLB"), ("sp2","ASTS"), ("sp3","LUNR"),
  # 방산 / AI방산
  ("df1","PLTR"), ("df2","LMT"), ("df3","RTX"), ("df4","KTOS"), ("df5","BWXT"),
  # 양자컴퓨팅
  ("qc1","IONQ"), ("qc2","RGTI"), ("qc3","QBTS"), ("qc4","QUBT"),
  # 클라우드 / SaaS
  ("cl1","CRM"), ("cl2","SNOW"), ("cl3","NOW"), ("cl4","MDB"),
]

today = date.today().isoformat()

try:
    with open("data.json","r") as f:
        data = json.load(f)
except:
    data = {}

if today not in data:
    data[today] = {}

success, failed = 0, 0
for stock_id, ticker in STOCKS:
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        q = r.json()
        cur = q.get("c", 0)
        pc  = q.get("pc", 0)
        if cur and cur > 0:
            data[today][stock_id] = round(cur, 4)
            print(f"  OK {ticker}: ${cur:.2f}")
            prev_dates = sorted(data.keys(), reverse=True)
            if len(prev_dates) > 1:
                prev_date = prev_dates[1]
                if stock_id not in data.get(prev_date, {}):
                    if prev_date not in data:
                        data[prev_date] = {}
                    data[prev_date][stock_id] = round(pc, 4)
            success += 1
        else:
            print(f"  SKIP {ticker}: no data")
            failed += 1
        time.sleep(0.3)
    except Exception as e:
        print(f"  FAIL {ticker}: {e}")
        failed += 1

with open("data.json","w") as f:
    json.dump(data, f, separators=(",",":"))

print(f"완료: {success}개 성공 / {failed}개 실패 / {today}")
