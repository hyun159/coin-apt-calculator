"""
코인-아파트 계산기
비트코인/이더리움/리플 실시간 시세 + 김해시 아파트 실거래가 비교
"""

from flask import Flask, render_template, jsonify
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import os
import pymysql

app = Flask(__name__)

# ===== 설정 =====
API_KEY = os.environ.get("APT_API_KEY", "55de5eac404756f92820d401d5cb4aad4cc558b10b3d15bb61e421df291f4aa0")
GIMHAE_CODE = "48250"

# ===== DB 설정 =====
DB_CONFIG = {
    "host": "10.0.2.14",
    "port": 3306,
    "user": "coinuser",
    "password": "asdf",
    "database": "coinapp",
    "charset": "utf8mb4",
}


def get_db():
    """DB 커넥션 반환"""
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)


def save_search_history(coin_name, coin_price):
    """검색 이력을 DB에 저장"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO search_history (coin_name, coin_price) VALUES (%s, %s)",
            (coin_name, coin_price)
        )
        conn.commit()
    except Exception as e:
        print(f"DB 저장 실패: {e}")
    finally:
        if conn:
            conn.close()


def get_coin_prices():
    """업비트 API로 코인 현재가 조회"""
    url = "https://api.upbit.com/v1/ticker"
    params = {"markets": "KRW-BTC,KRW-ETH,KRW-XRP"}

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        coins = {}
        name_map = {
            "KRW-BTC": {"name": "비트코인", "symbol": "BTC"},
            "KRW-ETH": {"name": "이더리움", "symbol": "ETH"},
            "KRW-XRP": {"name": "리플", "symbol": "XRP"},
        }

        for item in data:
            market = item["market"]
            info = name_map.get(market, {})
            coins[market] = {
                "name": info.get("name", market),
                "symbol": info.get("symbol", market),
                "price": item["trade_price"],
                "change": item["signed_change_rate"] * 100,
                "change_price": item["signed_change_price"],
                "high": item["high_price"],
                "low": item["low_price"],
                "volume": item["acc_trade_volume_24h"],
            }

        return coins
    except Exception as e:
        print(f"코인 시세 조회 실패: {e}")
        return {}


def get_apt_trades():
    """국토교통부 API로 김해시 아파트 실거래가 조회"""
    trades = []
    now = datetime.now()

    for i in range(3):
        target = now - timedelta(days=30 * i)
        deal_ymd = target.strftime("%Y%m")

        url = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
        params = {
            "serviceKey": API_KEY,
            "LAWD_CD": GIMHAE_CODE,
            "DEAL_YMD": deal_ymd,
            "pageNo": "1",
            "numOfRows": "100",
        }

        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()

            root = ET.fromstring(resp.content)

            for item in root.iter("item"):
                apt_name = item.findtext("aptNm", "").strip()
                deal_amount = item.findtext("dealAmount", "0").strip().replace(",", "")
                area = item.findtext("excluUseAr", "0").strip()
                deal_year = item.findtext("dealYear", "").strip()
                deal_month = item.findtext("dealMonth", "").strip()
                deal_day = item.findtext("dealDay", "").strip()
                floor_val = item.findtext("floor", "").strip()
                dong = item.findtext("umdNm", "").strip()
                build_year = item.findtext("buildYear", "").strip()
                road_name = item.findtext("roadNm", "").strip()

                try:
                    price = int(deal_amount) * 10000
                except ValueError:
                    continue

                trades.append({
                    "name": apt_name,
                    "dong": dong,
                    "price": price,
                    "price_man": int(deal_amount),
                    "area": float(area) if area else 0,
                    "floor": floor_val,
                    "date": f"{deal_year}.{deal_month.zfill(2)}.{deal_day.zfill(2)}",
                    "build_year": build_year,
                    "road": road_name,
                })

        except Exception as e:
            print(f"아파트 실거래가 조회 실패 ({deal_ymd}): {e}")
            continue

    trades.sort(key=lambda x: x["date"], reverse=True)
    return trades


# ===== 라우트 =====

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/coins")
def api_coins():
    """코인 시세 API + DB 이력 저장"""
    coins = get_coin_prices()

    for market, info in coins.items():
        save_search_history(info["name"], info["price"])

    return jsonify(coins)


@app.route("/api/apartments")
def api_apartments():
    """아파트 실거래가 API"""
    trades = get_apt_trades()
    return jsonify(trades)


@app.route("/api/history")
def api_history():
    """검색 이력 조회 API"""
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM search_history ORDER BY searched_at DESC LIMIT 50"
        )
        history = cursor.fetchall()

        for row in history:
            row["searched_at"] = str(row["searched_at"])

        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


# ===== 실행 =====

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)