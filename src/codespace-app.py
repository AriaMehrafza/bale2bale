from flask import Flask, Response
import requests
import threading
import time
import os

app = Flask(__name__)

API_URL = "https://tg.i-c-a.su/json"
channel_list = ["jadivarlog"]


def fetch_tel(channel_name: str, limit: int):
    url = f"{API_URL}/{channel_name}?limit={limit}"

    res = requests.get(url, timeout=30)
    res.raise_for_status()

    os.makedirs("datas/api_results", exist_ok=True)

    with open(f"datas/api_results/{channel_name}.json", "wb") as f:
        f.write(res.content)


def background_worker():
    while True:
        for channel in channel_list:
            try:
                fetch_tel(channel, 5)
                print(f"[OK] fetched {channel}")

            except Exception as e:
                print(f"[ERR] {channel}: {e}")

        time.sleep(180)


@app.route("/fetch_tel/<channel_name>")
def get_channel(channel_name):
    path = f"datas/api_results/{channel_name}.json"

    try:
        with open(path, "r") as f:
            return Response(f.read(), mimetype="application/json")

    except FileNotFoundError:
        return {"error": "not ready yet"}, 404


if __name__ == "__main__":
    t = threading.Thread(target=background_worker, daemon=True)
    t.start()

    app.run(port=8080)
