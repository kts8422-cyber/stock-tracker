import os, json, time, requests
from datetime import date, datetime

FINNHUB_KEY = os.environ["FINNHUB_KEY"]

STOCKS = [
    ("ai1","NVDA"),("ai2","MSFT"),("ai3","GOOGL"),("ai4","META"),("ai5","AMZN"),
    ("sc1","AMD"),("sc2","AVGO"),("sc3","TSM"),("sc4","ASML"),("sc5","QCOM"),
    ("dc1","VRT"),("dc2","EQIX"),("dc3","DLR"),("dc4","SMCI"),("dc5","ANET"),
    ("en1","CEG"),("en2","VST"),("en3","CCJ"),("en4","OKLO"),("en5","LEU"),
    ("sp1","RKLB"),("sp2","LMT"),("sp3","RTX"),("sp4","KTOS"),("sp5","ASTS"),
    ("qc1","IONQ"),("qc2","RGTI"),("qc3","QUBT"),("qc4","QBTS"),("qc5","IBM"),
    ("ar1","TSLA"),("ar2","MBLY"),("ar3","ISRG"),("ar4","PATH"),("ar5","ACHR"),
    ("fi1","V"),("fi2","COIN"),("fi3","SQ"),("fi4","PYPL"),("fi5","GS"),
    ("bi1","LLY"),("bi2","MRNA"),("bi3","RXRX"),("bi4","NVAX"),("bi5","GEHC"),
    ("cl1","CRM"),("cl2","SNOW"),("cl3","NOW"),("cl4","PLTR"),("cl5","MDB"),
]

today = date.today().isoformat()

# 기존 data.json 로드
try:
    with open("data.json", "r") as f:
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
        quote = r.json()
        current = quote.get("c", 0)
        prev_close = quote.get("pc", 0)

        if current and current > 0:
            data[today][stock_id] = round(current, 4)
            print(f"  ✅ {ticker}: ${current:.2f}")

            # 전일 종가도 저장 (없을 때만)
            prev_dates = sorted(data.keys(), reverse=True)
            if len(prev_dates) > 1:
                prev_date = prev_dates[1]
                if stock_id not in data.get(prev_date, {}):
                    if prev_date not in data:
                        data[prev_date] = {}
                    data[prev_date][stock_id] = round(prev_close, 4)
            success += 1
        else:
            print(f"  ⚠️  {ticker}: no data")
            failed += 1

        time.sleep(0.3)  # rate limit 여유있게

    except Exception as e:
        print(f"  ❌ {ticker}: {e}")
        failed += 1

with open("data.json", "w") as f:
    json.dump(data, f, separators=(",", ":"))

print(f"\n완료: {success}개 성공 / {failed}개 실패 / 날짜: {today}")
print(f"전체 저장 날짜 수: {len(data)}")
