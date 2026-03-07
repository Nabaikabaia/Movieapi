from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# API Creator Info
CREATOR = {
    "name": "Nabees",
    "channel": "https://whatsapp.com/channel/0029VawtjOXJpe8X3j3NCZ3j",
    "website": None,
    "twitter": None,
    "github": None
}

# Dictionary with all your movie categories (now with 16 categories!)
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
    # Add more categories here as you get them
}

# Category metadata for better responses
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

@app.route("/")
def home():
    return jsonify({
        "success": True,
        "creator": CREATOR,
        "message": "🎬 Movie Categories API - Your Ultimate Global Movie Database",
        "version": "5.1",
        "total_categories": len(CATEGORIES),
        "categories_count": len(CATEGORIES),
        "endpoints": {
            "/movies/<category>": "Get movies by category (add ?page=2&perPage=24 for pagination)",
            "/categories": "List all available categories with details",
            "/categories/<category>": "Get info about a specific category",
            "/search?q=<query>": "Search for categories",
            "/anime": "Legacy endpoint for anime",
            "/health": "Health check endpoint",
            "/about": "About the creator"
        },
        "regions_covered": list(set([info["region"] for info in CATEGORY_INFO.values()])),
        "available_categories": list(CATEGORIES.keys()),
        "quick_start": "Try /movies/turkish or /movies/indian?page=1",
        "support": "Join my WhatsApp channel for updates!"
    })

@app.route("/movies/<category>")
def get_movies(category):
    # Check if category exists
    if category not in CATEGORIES:
        return jsonify({
            "success": False,
            "creator": CREATOR,
            "error": "Category not found",
            "message": f"Available categories: {', '.join(CATEGORIES.keys())}",
            "available_categories": list(CATEGORIES.keys())
        }), 404
    
    category_id = CATEGORIES[category]
    page = request.args.get("page", 1)
    per_page = request.args.get("perPage", 12)
    
    # Validate pagination
    try:
        page = int(page)
        per_page = int(per_page)
        if per_page > 50:
            per_page = 50
        if page < 1:
            page = 1
    except ValueError:
        return jsonify({
            "success": False, 
            "creator": CREATOR,
            "error": "Invalid page or perPage value"
        }), 400
    
    url = f"https://h5-api.aoneroom.com/wefeed-h5api-bff/ranking-list/content?id={category_id}&page={page}&perPage={per_page}"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Client-Info": '{"timezone":"Africa/Lagos"}',
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjQ2ODM2NjU2ODU2NTc1ODQwMCwiYXRwIjozLCJleHQiOiIxNzcxNDE0NjY0IiwiZXhwIjoxNzc5MTkwNjY0LCJpYXQiOjE3NzE0MTQzNjR9.o6K7hQd3ii0dW-FvuoJ4JMwjTJfOvvlE6G-MTjUV73Y",
        "X-Request-Lang": "en"
    }

    try:
        print(f"🎬 Fetching {category} from API...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Check if API returned success
        if data.get("code") != 0:
            return jsonify({
                "success": False,
                "creator": CREATOR,
                "error": "API returned error",
                "message": data.get("message", "Unknown error")
            }), 500
        
        # Get category info
        category_info = CATEGORY_INFO.get(category, {
            "name": category.replace("-", " ").title(), 
            "region": "Unknown", 
            "type": "Unknown",
            "flag": "🎬"
        })
        
        # Get the title from response if available
        category_title = data.get("data", {}).get("title", category_info["name"])
        
        # Return the full JSON data with enhanced metadata and creator info
        return jsonify({
            "success": True,
            "creator": CREATOR,
            "category": category,
            "category_title": category_title,
            "category_info": category_info,
            "page": page,
            "perPage": per_page,
            "timestamp": response.headers.get("date"),
            "data": data.get("data", {})
        })
        
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "creator": CREATOR,
            "error": "Request timeout",
            "message": "The API took too long to respond"
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({
            "success": False,
            "creator": CREATOR,
            "error": "Failed to fetch data from source",
            "details": str(e)
        }), 500
    except ValueError as e:
        return jsonify({
            "success": False,
            "creator": CREATOR,
            "error": "Invalid JSON response from source",
            "details": str(e)
        }), 500

# Keep the original endpoint for backward compatibility
@app.route("/anime")
def get_anime():
    return get_movies("anime")

# List all available categories with details
@app.route("/categories")
def list_categories():
    categories_list = []
    for name, id in CATEGORIES.items():
        info = CATEGORY_INFO.get(name, {
            "name": name.replace("-", " ").title(), 
            "region": "Unknown", 
            "type": "Unknown",
            "flag": "🎬"
        })
        categories_list.append({
            "key": name,
            "name": info["name"],
            "flag": info["flag"],
            "id": id,
            "region": info["region"],
            "type": info["type"],
            "endpoint": f"/movies/{name}",
            "example": f"/movies/{name}?page=1"
        })
    
    # Sort by region then name
    categories_list.sort(key=lambda x: (x["region"], x["name"]))
    
    # Group by region for better organization
    by_region = {}
    for cat in categories_list:
        region = cat["region"]
        if region not in by_region:
            by_region[region] = []
        by_region[region].append(cat)
    
    return jsonify({
        "success": True,
        "creator": CREATOR,
        "count": len(categories_list),
        "total_categories": len(categories_list),
        "categories_by_region": by_region,
        "categories": categories_list
    })

# Get details about a specific category
@app.route("/categories/<category>")
def category_info(category):
    if category not in CATEGORIES:
        return jsonify({
            "success": False,
            "creator": CREATOR,
            "error": "Category not found",
            "available_categories": list(CATEGORIES.keys())
        }), 404
    
    info = CATEGORY_INFO.get(category, {
        "name": category.replace("-", " ").title(), 
        "region": "Unknown", 
        "type": "Unknown",
        "flag": "🎬"
    })
    
    return jsonify({
        "success": True,
        "creator": CREATOR,
        "category": {
            "key": category,
            "name": info["name"],
            "flag": info["flag"],
            "id": CATEGORIES[category],
            "region": info["region"],
            "type": info["type"],
            "endpoint": f"/movies/{category}",
            "docs": f"Use /movies/{category}?page=1 to get content"
        }
    })

# Health check endpoint
@app.route("/health")
def health_check():
    return jsonify({
        "success": True,
        "creator": CREATOR,
        "status": "healthy",
        "categories_available": len(CATEGORIES),
        "timestamp": requests.utils.formatdate(timeval=None, localtime=False, usegmt=True)
    })

# About the creator
@app.route("/about")
def about():
    return jsonify({
        "success": True,
        "creator": CREATOR,
        "message": "Movie Categories API - Built with ❤️ by Nabees",
        "support": "Join my WhatsApp channel for updates, new features, and category additions!",
        "channel": CREATOR["channel"],
        "categories_count": len(CATEGORIES),
        "categories": list(CATEGORIES.keys())
    })

# Search across categories
@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    if not query or len(query) < 2:
        return jsonify({
            "success": False,
            "creator": CREATOR,
            "error": "Search query must be at least 2 characters"
        }), 400
    
    # Search in category names, regions, and types
    results = []
    for category in CATEGORIES.keys():
        info = CATEGORY_INFO.get(category, {
            "name": category.replace("-", " ").title(), 
            "region": "Unknown", 
            "type": "Unknown",
            "flag": "🎬"
        })
        
        if (query in category.lower() or 
            query in info["name"].lower() or 
            query in info["region"].lower() or
            query in info["type"].lower()):
            
            results.append({
                "category": category,
                "name": info["name"],
                "flag": info["flag"],
                "region": info["region"],
                "type": info["type"],
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
    port = int(os.environ.get("PORT", 10000))
    print("=" * 60)
    print("🌍 GLOBAL MOVIE API - 16 CATEGORIES")
    print("=" * 60)
    print(f"👤 Creator: {CREATOR['name']}")
    print(f"📱 Channel: {CREATOR['channel']}")
    print(f"📡 Port: {port}")
    print(f"🎯 Total Categories: {len(CATEGORIES)}")
    print("\n📋 Categories by Region:")
    
    by_region = {}
    for key, info in CATEGORY_INFO.items():
        region = info["region"]
        if region not in by_region:
            by_region[region] = []
        by_region[region].append(f"{info['flag']} {info['name']}")
    
    for region, cats in by_region.items():
        print(f"\n  {region}:")
        for cat in cats:
            print(f"    • {cat}")
    
    print("\n" + "=" * 60)
    print("🚀 Server starting...")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=True)
