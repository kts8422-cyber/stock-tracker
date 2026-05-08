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
  # AI / 빅테크
  ("ai1","MSFT"),("ai2","META"),("ai3","GOOGL"),("ai4","AAPL"),("ai5","AMZN"),("ai6","TSLA"),
  # 반도체
  ("sc1","NVDA"),("sc2","QCOM"),("sc3","TSM"),("sc4","ASML"),("sc5","MU"),
  ("sc6","INTC"),("sc7","AVGO"),("sc8","SNDK"),("sc9","WDC"),("sc10","AMD"),("sc11","MRVL"),
  # 데이터센터 / 전력
  ("dc1","VRT"),("dc2","ETN"),("dc3","GEV"),("dc4","LITE"),("dc5","IREN"),("dc6","POWL"),
  # 원전
  ("en1","UEC"),("en2","CEG"),("en3","CCJ"),("en4","OKLO"),
  ("en5","LEU"),("en6","UUUU"),("en7","SMR"),("en8","NNE"),
  # 우주
  ("sp1","RKLB"),("sp2","ASTS"),("sp3","LUNR"),("sp4","VOYG"),
  ("sp5","BKSY"),("sp6","PL"),("sp7","FLY"),("sp8","RDW"),
  # 방산
  ("df1","PLTR"),("df2","RTX"),("df3","LMT"),("df4","BWXT"),
  ("df5","KTOS"),("df6","LHX"),("df7","NOC"),
  # 양자컴퓨팅
  ("qc1","QBTS"),("qc2","QUBT"),("qc3","RGTI"),("qc4","IONQ"),
  ("qc5","LAES"),("qc6","BTQ"),("qc7","XNDU"),("qc8","HON"),
  # 클라우드 / SaaS
  ("cl1","MDB"),("cl2","SNOW"),("cl3","NOW"),("cl4","CRM"),("cl5","P"),("cl6","CRWV"),
]

try:
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"기존 data.json: {len(data)}일치 로드")
except FileNotFoundError:
    data = {}
    print("data.json 없음 → 새로 생성")
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
        cur  = float(q.get("c",  0) or 0)
        pc   = float(q.get("pc", 0) or 0)
        open_= float(q.get("o",  0) or 0)
        high = float(q.get("h",  0) or 0)
        low  = float(q.get("l",  0) or 0)

        if cur > 0:
            # 현재가 (기존 HTML이 읽는 값 — 구조 그대로 유지)
            data[today][stock_id] = round(cur, 4)
            # 시가/고가/저가 별도 키로 저장 (html은 아직 무시)
            if open_ > 0: data[today][stock_id+'_o'] = round(open_, 4)
            if high  > 0: data[today][stock_id+'_h'] = round(high,  4)
            if low   > 0: data[today][stock_id+'_l'] = round(low,   4)

            # 전일 종가 저장 (없을 때만)
            sorted_dates = sorted(data.keys(), reverse=True)
            if len(sorted_dates) > 1:
                prev_date = sorted_dates[1]
                if stock_id not in data.get(prev_date, {}):
                    if prev_date not in data:
                        data[prev_date] = {}
                    data[prev_date][stock_id] = round(pc, 4)

            print(f"  OK  {ticker:6s}: ${cur:.2f}  (o:{open_:.2f} h:{high:.2f} l:{low:.2f})")
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
    lines = ["{"]
    for i, key in enumerate(sorted_keys):
        val = json.dumps(data[key], separators=(",", ":"), ensure_ascii=False)
        comma = "," if i < len(sorted_keys)-1 else ""
        lines.append(f'  "{key}":{val}{comma}')
    lines.append("}")
    with open("data.json", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n저장 완료: {today} / 성공 {success}개 / 실패 {failed}개")
    print(f"전체 날짜: {sorted_keys}")
except Exception as e:
    print(f"저장 실패: {e}")
    sys.exit(1)
