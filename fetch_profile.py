import os, json, requests, time, sys
from datetime import datetime, timezone, timedelta

FINNHUB_KEY = os.environ.get("FINNHUB_KEY", "")
if not FINNHUB_KEY:
    print("ERROR: FINNHUB_KEY 없음")
    sys.exit(1)

STOCKS = [
  ("ai1","MSFT"),("ai2","META"),("ai3","GOOGL"),("ai4","AAPL"),("ai5","AMZN"),("ai6","TSLA"),
  ("sc1","NVDA"),("sc2","QCOM"),("sc3","TSM"),("sc4","ASML"),("sc5","MU"),
  ("sc6","INTC"),("sc7","AVGO"),("sc8","SNDK"),("sc9","WDC"),("sc10","AMD"),("sc11","MRVL"),
  ("dc1","VRT"),("dc2","ETN"),("dc3","GEV"),("dc4","LITE"),("dc5","IREN"),("dc6","POWL"),
  ("en1","UEC"),("en2","CEG"),("en3","CCJ"),("en4","OKLO"),
  ("en5","LEU"),("en6","UUUU"),("en7","SMR"),("en8","NNE"),
  ("sp1","RKLB"),("sp2","ASTS"),("sp3","LUNR"),("sp4","VOYG"),
  ("sp5","BKSY"),("sp6","PL"),("sp7","FLY"),("sp8","RDW"),
  ("df1","PLTR"),("df2","RTX"),("df3","LMT"),("df4","BWXT"),
  ("df5","KTOS"),("df6","LHX"),("df7","NOC"),
  ("qc1","QBTS"),("qc2","QUBT"),("qc3","RGTI"),("qc4","IONQ"),
  ("qc5","LAES"),("qc6","BTQ"),("qc7","XNDU"),("qc8","HON"),
  ("cl1","MDB"),("cl2","SNOW"),("cl3","NOW"),("cl4","CRM"),("cl5","P"),("cl6","CRWV"),
]

profile = {}
success, failed = 0, 0

for stock_id, ticker in STOCKS:
    try:
        url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker}&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        d = r.json()
        shares = float(d.get("shareOutstanding", 0) or 0)
        profile[stock_id] = {
            "ticker": ticker,
            "name": d.get("name", ticker),
            "shares": round(shares, 4),
        }
        print(f"  OK  {ticker:6s}: {shares:.2f}M주")
        success += 1
    except Exception as e:
        print(f"  FAIL {ticker:6s}: {e}")
        profile[stock_id] = {"ticker": ticker, "shares": 0}
        failed += 1
    time.sleep(0.5)

KST = timezone(timedelta(hours=9))
profile["_updated"] = datetime.now(KST).strftime("%Y-%m-%d %H:%M")

with open("profile.json", "w", encoding="utf-8") as f:
    json.dump(profile, f, indent=2, ensure_ascii=False)

print(f"\n저장 완료: {success}개 성공 / {failed}개 실패")
