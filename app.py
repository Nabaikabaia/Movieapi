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

# Base URL for video sources
VIDEO_BASE_URL = "https://vid.davidxtech.de/api/sources"
SEARCH_BASE_URL = "https://vid.davidxtech.de/api/search"
INFO_BASE_URL = "https://vid.davidxtech.de/api/info"

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

# Headers for category API requests (aoneroom.com)
def get_category_headers():
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Client-Info": '{"timezone":"Africa/Lagos"}',
        "Authorization": os.environ.get("API_TOKEN", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjQ2ODM2NjU2ODU2NTc1ODQwMCwiYXRwIjozLCJleHQiOiIxNzcxNDE0NjY0IiwiZXhwIjoxNzc5MTkwNjY0LCJpYXQiOjE3NzE0MTQzNjR9.o6K7hQd3ii0dW-FvuoJ4JMwjTJfOvvlE6G-MTjUV73Y"),
        "X-Request-Lang": "en"
    }

# Headers for vid.davidxtech.de API requests (FIXES 403 ERROR)
def get_vid_headers():
    """Headers required to access vid.davidxtech.de - fixes 403 Forbidden error"""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://vid.davidxtech.de/",
        "Origin": "https://vid.davidxtech.de",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "success": True,
        "creator": CREATOR,
        "message": "🎬 Nabees Movie API - Your Ultimate Global Movie Database",
        "version": "7.2",
        "total_categories": len(CATEGORIES),
        "endpoints": {
            # Category endpoints
            "/movies/<category>": "Get movies by category (e.g., /movies/k-drama)",
            "/categories": "List all available categories",
            
            # Video source endpoints
            "/api/series": "GET /api/series?id=XXX&season=1&episode=1 - Get series video sources",
            "/api/movie": "GET /api/movie?id=XXX - Get movie video sources",
            "/api/sources/<movie_id>": "GET /api/sources/12345?season=1&episode=1 - Get sources by ID",
            
            # Movie info endpoint (NEW)
            "/api/info/<movie_id>": "GET /api/info/1216407338207298384 - Get detailed movie/series info",
            
            # Search endpoint
            "/api/search": "GET /api/search?q=avengers&page=1 - Search for movies and series",
            
            # Info endpoints
            "/about": "About the creator",
            "/health": "Health check endpoint",
            "/search": "GET /search?q=anime - Search for categories"
        },
        "examples": {
            "search_movies": "/api/search?q=avengers&page=1",
            "get_series": "/api/series?id=12345&season=1&episode=1",
            "get_movie": "/api/movie?id=4191963760367656968",
            "get_sources_movie": "/api/sources/4191963760367656968",
            "get_sources_series": "/api/sources/12345?season=1&episode=1",
            "get_movie_info": "/api/info/1216407338207298384",
            "get_category": "/movies/k-drama?page=1&perPage=20",
            "search_categories": "/search?q=korea"
        },
        "available_categories": list(CATEGORIES.keys())
    })

# ============ CATEGORY ENDPOINTS ============

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
        response = requests.get(url, headers=get_category_headers(), timeout=10)
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

@app.route('/search', methods=['GET'])
def search_categories():
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

# ============ VIDEO SOURCE ENDPOINTS ============

@app.route("/api/series", methods=['GET'])
def get_series():
    """
    Get series video sources
    Required: id, season, episode
    Example: /api/series?id=12345&season=1&episode=1
    """
    movie_id = request.args.get("id")
    season = request.args.get("season")
    episode = request.args.get("episode")

    if not movie_id or not season or not episode:
        return jsonify({
            "status": 400,
            "success": False,
            "message": "id, season and episode are required",
            "example": "/api/series?id=12345&season=1&episode=1",
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"]
        }), 400

    url = f"{VIDEO_BASE_URL}/{movie_id}?season={season}&episode={episode}"

    try:
        print(f"Fetching series: ID={movie_id}, S{season}E{episode}")
        # Use vid headers to avoid 403 error
        r = requests.get(url, headers=get_vid_headers(), timeout=10)
        r.raise_for_status()
        data = r.json()

        return jsonify({
            "status": 200,
            "success": True,
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"],
            "type": "series",
            "movie_id": movie_id,
            "season": season,
            "episode": episode,
            "results": data.get("results"),
            "subtitles": data.get("subtitles")
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": 500,
            "success": False,
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"],
            "error": f"Failed to fetch series: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "status": 500,
            "success": False,
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"],
            "error": str(e)
        }), 500


@app.route("/api/movie", methods=['GET'])
def get_movie():
    """
    Get movie video sources
    Required: id
    Example: /api/movie?id=4191963760367656968
    """
    movie_id = request.args.get("id")

    if not movie_id:
        return jsonify({
            "status": 400,
            "success": False,
            "message": "movie id required",
            "example": "/api/movie?id=4191963760367656968",
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"]
        }), 400

    url = f"{VIDEO_BASE_URL}/{movie_id}"

    try:
        print(f"Fetching movie: ID={movie_id}")
        # Use vid headers to avoid 403 error
        r = requests.get(url, headers=get_vid_headers(), timeout=10)
        r.raise_for_status()
        data = r.json()

        return jsonify({
            "status": 200,
            "success": True,
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"],
            "type": "movie",
            "movie_id": movie_id,
            "results": data.get("results"),
            "subtitles": data.get("subtitles")
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": 500,
            "success": False,
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"],
            "error": f"Failed to fetch movie: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "status": 500,
            "success": False,
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"],
            "error": str(e)
        }), 500


@app.route("/api/sources/<movie_id>", methods=['GET'])
def get_sources(movie_id):
    """
    Get sources by movie ID
    For movies: /api/sources/4191963760367656968
    For series: /api/sources/12345?season=1&episode=1
    """
    season = request.args.get("season")
    episode = request.args.get("episode")
    
    # Build URL based on whether season/episode are provided
    url = f"{VIDEO_BASE_URL}/{movie_id}"
    if season and episode:
        url += f"?season={season}&episode={episode}"
        content_type = "series"
    else:
        content_type = "movie"
    
    try:
        print(f"Fetching sources for ID: {movie_id} (type: {content_type})")
        # Use vid headers to avoid 403 error
        r = requests.get(url, headers=get_vid_headers(), timeout=10)
        r.raise_for_status()
        data = r.json()
        
        # Add creator info to response
        return jsonify({
            "status": 200,
            "success": True,
            "creator": CREATOR["name"],
            "channel": CREATOR["channel"],
            "type": content_type,
            "movie_id": movie_id,
            "season": season if season else None,
            "episode": episode if episode else None,
            "results": data.get("results"),
            "subtitles": data.get("subtitles")
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": 500,
            "success": False,
            "creator": CREATOR["name"],
            "channel": CREATOR["channel"],
            "error": f"Failed to fetch sources: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "status": 500,
            "success": False,
            "creator": CREATOR["name"],
            "channel": CREATOR["channel"],
            "error": str(e)
        }), 500


# ============ MOVIE INFO ENDPOINT (NEW) ============

@app.route("/api/info/<movie_id>", methods=['GET'])
def get_movie_info(movie_id):
    """
    Get detailed information about a movie or series by ID
    Includes: title, description, cast, seasons, ratings, etc.
    Example: /api/info/1216407338207298384
    """
    if not movie_id:
        return jsonify({
            "status": 400,
            "success": False,
            "message": "movie_id is required",
            "example": "/api/info/1216407338207298384",
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"]
        }), 400

    url = f"{INFO_BASE_URL}/{movie_id}"

    try:
        print(f"Fetching movie info for ID: {movie_id}")
        # Use vid headers to avoid 403 error
        response = requests.get(url, headers=get_vid_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()

        # Add your creator info to the response
        data["nabees_creator"] = CREATOR["name"]
        data["nabees_channel"] = CREATOR["channel"]

        return jsonify(data)

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": 500,
            "success": False,
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"],
            "error": f"Failed to fetch movie info: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "status": 500,
            "success": False,
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"],
            "error": str(e)
        }), 500


# ============ SEARCH ENDPOINT ============

@app.route("/api/search", methods=['GET'])
def search_movies():
    """
    Search for movies and series by title
    Required: q (query)
    Optional: page (default: 1)
    Example: /api/search?q=avengers&page=1
    """
    query = request.args.get("q")
    page = request.args.get("page", 1)

    if not query:
        return jsonify({
            "status": 400,
            "success": False,
            "message": "search query (q) is required",
            "example": "/api/search?q=avengers&page=1",
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"]
        }), 400

    try:
        page = int(page)
    except ValueError:
        return jsonify({
            "status": 400,
            "success": False,
            "message": "page must be a number",
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"]
        }), 400

    url = f"{SEARCH_BASE_URL}/{query}/?page={page}"

    try:
        print(f"Searching for: '{query}', page {page}")
        # Use vid headers for search as well
        response = requests.get(url, headers=get_vid_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()

        # Format the results
        formatted_results = []
        items = data.get("results", {}).get("items", [])

        for item in items:
            # Determine content type (subjectType: 2 = Series, others = Movie)
            content_type = "Series" if item.get("subjectType") == 2 else "Movie"
            
            movie = {
                "title": item.get("title"),
                "type": content_type,
                "genre": item.get("genre"),
                "release_date": item.get("releaseDate"),
                "country": item.get("countryName"),
                "imdb_rating": item.get("imdbRatingValue"),
                "thumbnail": item.get("thumbnail"),
                "detail_path": item.get("detailPath"),
                "subject_id": item.get("subjectId"),
                "description": item.get("descriptionShort")
            }
            
            # Only add if we have essential data
            if movie["title"] and movie["subject_id"]:
                formatted_results.append(movie)

        return jsonify({
            "status": 200,
            "success": True,
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"],
            "query": query,
            "page": page,
            "total_results": len(formatted_results),
            "results": formatted_results
        })

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": 500,
            "success": False,
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"],
            "error": f"Failed to search: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "status": 500,
            "success": False,
            "creator": CREATOR["name"],
            "whatsapp_channel": CREATOR["channel"],
            "error": str(e)
        }), 500


# ============ INFO ENDPOINTS ============

@app.route('/about', methods=['GET'])
def about():
    return jsonify({
        "success": True,
        "creator": CREATOR,
        "message": "Movie API - Built with ❤️ by Nabees",
        "channel": CREATOR["channel"],
        "categories_count": len(CATEGORIES),
        "version": "7.2"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "success": True,
        "creator": CREATOR,
        "status": "healthy",
        "timestamp": time.time()
    })

if __name__ == "__main__":
    # Use PORT from environment, default to 10000
    port = int(os.environ.get("PORT", 10000))
    
    print("=" * 70)
    print("🎬 NABEES MOVIE API - COMPLETE EDITION v7.2")
    print("=" * 70)
    print(f"👤 Creator: {CREATOR['name']}")
    print(f"📱 Channel: {CREATOR['channel']}")
    print(f"📡 Port: {port}")
    print(f"🎯 Categories: {len(CATEGORIES)}")
    print("=" * 70)
    print("🚀 ENDPOINTS:")
    print("   📂 CATEGORIES:")
    print("      ├─ /categories - List all categories")
    print("      ├─ /movies/<category> - Get movies by category")
    print("      └─ /search?q=<query> - Search categories")
    print("")
    print("   🔍 SEARCH:")
    print("      └─ /api/search?q=<query>&page=1 - Search movies & series")
    print("")
    print("   ℹ️  MOVIE INFO (NEW!):")
    print("      └─ /api/info/<movie_id> - Get detailed movie/series info")
    print("")
    print("   🎬 VIDEO SOURCES (403 FIXED ✅):")
    print("      ├─ /api/movie?id=XXX - 🍿 GET MOVIE (id only)")
    print("      ├─ /api/series?id=XXX&season=1&episode=1 - 📺 GET SERIES")
    print("      └─ /api/sources/<movie_id> - 🔗 GET SOURCES (works for both)")
    print("")
    print("   ℹ️  INFO:")
    print("      ├─ / - Home page")
    print("      ├─ /about - About creator")
    print("      └─ /health - Health check")
    print("=" * 70)
    print("📝 EXAMPLES:")
    print("   • Movie Info: curl http://localhost:10000/api/info/1216407338207298384")
    print("   • Search:     curl http://localhost:10000/api/search?q=avengers")
    print("   • Movie:      curl http://localhost:10000/api/movie?id=4191963760367656968")
    print("   • Series:     curl http://localhost:10000/api/series?id=12345&season=1&episode=1")
    print("   • K-Drama:    curl http://localhost:10000/movies/k-drama?page=1")
    print("=" * 70)
    print("🚀 Server starting...")
    print("=" * 70)
    
    # Bind to 0.0.0.0 to accept all connections
    app.run(host='0.0.0.0', port=port, debug=False)
