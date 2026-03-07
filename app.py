import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

CATEGORY_ID = "62133389738001440"
API_URL = "https://h5-api.aoneroom.com/wefeed-h5api-bff/ranking-list/content"


@app.route("/anime")
def get_anime_ids():

    page = request.args.get("page", default=1, type=int)

    headers = {
        "Accept": "application/json",
        "X-Client-Info": '{"timezone":"Africa/Lagos"}',
        "X-Request-Lang": "en"
    }

    params = {
        "id": CATEGORY_ID,
        "page": page,
        "perPage": 12
    }

    res = requests.get(API_URL, headers=headers, params=params)
    data = res.json()

    subject_ids = [item["subjectId"] for item in data["data"]["subjectList"]]

    return jsonify({
        "category": "anime",
        "page": page,
        "per_page": 12,
        "subject_ids": subject_ids,
        "has_more": data["data"]["pager"]["hasMore"],
        "next_page": data["data"]["pager"]["nextPage"]
    })


@app.route("/")
def home():
    return jsonify({
        "message": "Movie Subject ID API",
        "endpoint": "/anime?page=1"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
