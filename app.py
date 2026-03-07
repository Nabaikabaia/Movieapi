from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Change this ID to your category ID
CATEGORY_ID = "62133389738001440"

@app.route("/anime")
def get_anime_subject_ids():
    page = request.args.get("page", 1)
    url = f"https://h5-api.aoneroom.com/wefeed-h5api-bff/ranking-list/content?id={CATEGORY_ID}&page={page}&perPage=12"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Client-Info": '{"timezone":"Africa/Lagos"}',
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjQ2ODM2NjU2ODU2NTc1ODQwMCwiYXRwIjozLCJleHQiOiIxNzcxNDE0NjY0IiwiZXhwIjoxNzc5MTkwNjY0LCJpYXQiOjE3NzE0MTQzNjR9.o6K7hQd3ii0dW-FvuoJ4JMwjTJfOvvlE6G-MTjUV73Y",  # replace with your token
        "X-Request-Lang": "en"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    # Extract only subjectIds
    subject_ids = [item["subjectId"] for item in data.get("data", {}).get("subjectList", [])]

    return jsonify({
        "page": page,
        "subjectIds": subject_ids
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
