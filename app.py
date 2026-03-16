from flask import Flask, request, jsonify
import requests
import os
import time

app = Flask(__name__)

# API Creator Info
CREATOR = {
    "name": "Nabees",
    "channel": "https://whatsapp.com/channel/0029VawtjOXJpe8X3j3NCZ3j",
    "website": "https://nabees.online",
    "twitter": None,
    "github": None
}

# Dictionary with all your movie categories
CATEGORIES = {
    "anime": "62133389738001440",
    "nollywood": "8216283712045280",
    "black-drama": "8505361996374835640", 
    "k-drama": "4380734070238626200",
    "sa-drama": "4307848214843217008",
    "animation": "7132534597631837112",
    "bollywood": "414907768299210008",
    "c-drama": "173752404280836544",
    "thai-drama": "1164329479448281992",
    "returning-tv": "8109661952110199232",
    "top-list": "1232643093049001320",
    "new-tv": "2529702013798074864",
    "popular": "997144265920760504",
    "showmax": "2076266324048625696",
    "turkish": "9193088611682599936",
    "indian": "3859721901924910512"
}

# Category metadata
CATEGORY_INFO = {
    "anime": {"name": "Anime", "region": "Japan", "type": "Animation", "flag": "🇯🇵"},
    "nollywood": {"name": "Nollywood", "region": "Nigeria", "type": "Movies", "flag": "🇳🇬"},
    "black-drama": {"name": "Black Drama", "region": "USA/UK", "type": "TV Series", "flag": "🎭"},
    "k-drama": {"name": "K-Drama", "region": "South Korea", "type": "TV Series", "flag": "🇰🇷"},
    "sa-drama": {"name": "South African Drama", "region": "South Africa", "type": "TV Series", "flag": "🇿🇦"},
    "animation": {"name": "Animation", "region": "Various", "type": "Animated", "flag": "🎨"},
    "bollywood": {"name": "Bollywood", "region": "India", "type": "Movies", "flag": "🇮🇳"},
    "c-drama": {"name": "C-Drama", "region": "China", "type": "TV Series", "flag": "🇨🇳"},
    "thai-drama": {"name": "Thai Drama", "region": "Thailand", "type": "TV Series", "flag": "🇹🇭"},
    "returning-tv": {"name": "Returning TV Shows", "region": "Various", "type": "TV Series", "flag": "📺"},
    "top-list": {"name": "Top Trending", "region": "Global", "type": "Mixed", "flag": "🔥"},
    "new-tv": {"name": "New TV Shows", "region": "Various", "type": "TV Series", "flag": "🆕"},
    "popular": {"name": "Popular Movies 2025", "region": "Various", "type": "Movies", "flag": "⭐"},
    "showmax": {"name": "Showmax Originals", "region": "Africa", "type": "Originals", "flag": "📱"},
    "turkish": {"name": "Turkish Drama", "region": "Turkey", "type": "TV Series", "flag": "🇹🇷"},
    "indian": {"name": "South Indian Movies", "region": "India", "type": "Movies", "flag": "🇮🇳"}
}

# Headers for API requests
def get_headers():
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Client-Info": '{"timezone":"Africa/Lagos"}',
        "Authorization": os.environ.get("API_TOKEN", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjQ2ODM2NjU2ODU2NTc1ODQwMCwiYXRwIjozLCJleHQiOiIxNzcxNDE0NjY0IiwiZXhwIjoxNzc5MTkwNjY0LCJpYXQiOjE3NzE0MTQzNjR9.o6K7hQd3ii0dW-FvuoJ4JMwjTJfOvvlE6G-MTjUV73Y"),
        "X-Request-Lang": "en"
    }

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "success": True,
        "creator": CREATOR,
        "message": "🎬 Nabees Movie Categories API - Your Ultimate Global Movie Database",
        "version": "5.1",
        "total_categories": len(CATEGORIES),
        "endpoints": {
            "/movies/<category>": "Get movies by category",
            "/categories": "List all available categories",
            "/about": "About the creator",
            "/health": "Health check endpoint",
            "/search?q=<query>": "Search for categories"
        },
        "available_categories": list(CATEGORIES.keys())
    })

@app.route('/movies/<category>', methods=['GET'])
def get_movies(category):
    if category not in CATEGORIES:
        return jsonify({
            "success": False,
            "creator": CREATOR,
            "error": "Category not found",
            "available_categories": list(CATEGORIES.keys())
        }), 404
    
    category_id = CATEGORIES[category]
    page = request.args.get("page", 1)
    per_page = request.args.get("perPage", 12)
    
    try:
        page = int(page)
        per_page = int(per_page)
        if per_page > 50:
            per_page = 50
    except ValueError:
        return jsonify({"success": False, "error": "Invalid page value"}), 400
    
    url = f"https://h5-api.aoneroom.com/wefeed-h5api-bff/ranking-list/content?id={category_id}&page={page}&perPage={per_page}"
    
    try:
        print(f"Fetching {category}...")
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != 0:
            return jsonify({"success": False, "error": "API error"}), 500
        
        category_info = CATEGORY_INFO.get(category, {"name": category, "flag": "🎬"})
        
        return jsonify({
            "success": True,
            "creator": CREATOR,
            "category": category,
            "category_info": category_info,
            "page": page,
            "data": data.get("data", {})
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "creator": CREATOR,
            "error": str(e)
        }), 500

@app.route('/categories', methods=['GET'])
def list_categories():
    categories_list = []
    for name, id in CATEGORIES.items():
        info = CATEGORY_INFO.get(name, {"name": name, "flag": "🎬"})
        categories_list.append({
            "key": name,
            "name": info["name"],
            "flag": info["flag"],
            "id": id,
            "region": info.get("region", "Unknown"),
            "type": info.get("type", "Unknown"),
            "endpoint": f"/movies/{name}"
        })
    
    return jsonify({
        "success": True,
        "creator": CREATOR,
        "count": len(categories_list),
        "categories": categories_list
    })

@app.route('/about', methods=['GET'])
def about():
    return jsonify({
        "success": True,
        "creator": CREATOR,
        "message": "Movie Categories API - Built with ❤️ by Nabees",
        "channel": CREATOR["channel"],
        "categories_count": len(CATEGORIES)
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "success": True,
        "creator": CREATOR,
        "status": "healthy",
        "timestamp": time.time()
    })

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get("q", "").lower()
    if not query or len(query) < 2:
        return jsonify({"success": False, "error": "Query too short"}), 400
    
    results = []
    for category in CATEGORIES.keys():
        info = CATEGORY_INFO.get(category, {"name": category})
        if query in category.lower() or query in info["name"].lower():
            results.append({
                "category": category,
                "name": info["name"],
                "flag": info.get("flag", "🎬"),
                "endpoint": f"/movies/{category}"
            })
    
    return jsonify({
        "success": True,
        "creator": CREATOR,
        "query": query,
        "results_count": len(results),
        "results": results
    })

if __name__ == "__main__":
    # CRITICAL FIX: Use PORT from environment, default to 10000
    port = int(os.environ.get("PORT", 10000))
    
    print("=" * 60)
    print("🌍 GLOBAL MOVIE API")
    print("=" * 60)
    print(f"👤 Creator: {CREATOR['name']}")
    print(f"📱 Channel: {CREATOR['channel']}")
    print(f"📡 Port: {port}")
    print(f"🎯 Categories: {len(CATEGORIES)}")
    print("=" * 60)
    print("🚀 Server starting...")
    print("=" * 60)
    
    # Bind to 0.0.0.0 to accept all connections
    app.run(host='0.0.0.0', port=port, debug=False)
