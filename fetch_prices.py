import os, json, time, requests, sys
from datetime import datetime, timezone, timedelta

FINNHUB_KEY = os.environ.get("FINNHUB_KEY", "")
if not FINNHUB_KEY:
    print("ERROR: FINNHUB_KEY 없음")
    sys.exit(1)

KST = timezone(timedelta(hours=9))
today = datetime.now(KST).strftime("%Y-%m-%d")
print(f"날짜 (KST): {today}")

STOCKS = [
  ("ai1","MSFT"), ("ai2","GOOGL"), ("ai3","META"), ("ai4","AMZN"), ("ai5","AAPL"),
  ("sc1","NVDA"), ("sc2","SOXL"), ("sc3","INTC"), ("sc4","MU"), ("sc5","AVGO"),
  ("sc6","ASML"), ("sc7","TSM"), ("sc8","QCOM"),
  ("dc1","VRT"), ("dc2","EQIX"), ("dc3","GEV"), ("dc4","ETN"), ("dc5","DLR"),
  ("en1","CEG"), ("en2","CCJ"), ("en3","OKLO"), ("en4","LEU"), ("en5","UEC"), ("en6","AR"),
  ("sp1","RKLB"), ("sp2","ASTS"), ("sp3","LUNR"),
  ("df1","PLTR"), ("df2","LMT"), ("df3","RTX"), ("df4","KTOS"), ("df5","BWXT"),
  ("qc1","IONQ"), ("qc2","RGTI"), ("qc3","QBTS"), ("qc4","QUBT"),
  ("cl1","CRM"), ("cl2","SNOW"), ("cl3","NOW"), ("cl4","MDB"),
]

try:
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"기존 data.json: {len(data)}일치 로드")
except FileNotFoundError:
    data = {}
    print("data.json 없음 -> 새로 생성")
except Exception as e:
    data = {}
    print(f"로드 실패: {e}")

if today not in data:
    data[today] = {}

success, failed = 0, 0
for stock_id, ticker in STOCKS:
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        q = r.json()
        cur = float(q.get("c", 0) or 0)
        pc  = float(q.get("pc", 0) or 0)

        if cur > 0:
            data[today][stock_id] = round(cur, 4)
            sorted_dates = sorted(data.keys(), reverse=True)
            if len(sorted_dates) > 1:
                prev_date = sorted_dates[1]
                if stock_id not in data.get(prev_date, {}):
                    if prev_date not in data:
                        data[prev_date] = {}
                    data[prev_date][stock_id] = round(pc, 4)
            print(f"  OK  {ticker:6s}: ${cur:.2f}")
            success += 1
        else:
            print(f"  SKIP {ticker:6s}: 가격 없음")
            failed += 1

    except Exception as e:
        print(f"  FAIL {ticker:6s}: {e}")
        failed += 1

    time.sleep(0.4)

try:
    sorted_keys = sorted(data.keys())
    lines = []
    lines.append("{")
    for i, key in enumerate(sorted_keys):
        val = json.dumps(data[key], separators=(",", ":"), ensure_ascii=False)
        comma = "," if i < len(sorted_keys) - 1 else ""
        lines.append(f'  "{key}":{val}{comma}')
    lines.append("}")
    output = "\n".join(lines)
    with open("data.json", "w", encoding="utf-8") as f:
        f.write(output)
    print(f"저장 완료: {today} / 성공 {success}개 / 실패 {failed}개")
    print(f"전체 날짜: {sorted_keys}")
except Exception as e:
    print(f"저장 실패: {e}")
    sys.exit(1)
