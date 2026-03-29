from flask import Flask, request, jsonify, Response, stream_with_context
from collections import OrderedDict
import requests
import json
import os
import time

app = Flask(__name__)

# ============================================
# BRANDING CONFIGURATION
# ============================================
BRANDING = {
    "status": 200,
    "success": True,
    "creator": "Nabees Tech",
    "developer": "Nabees",
    "whatsapp_channel": "https://whatsapp.com/channel/0029VawtjOXJpe8X3j3NCZ3j",
    "website": "https://nabees.online",
    "telegram": "https://t.me/nabeestech",
    "github": "https://github.com/Nabaikabaia",
    "support_email": "nabees.dev@gmail.com",
    "api_name": "Nabees Movie API",
    "api_version": "2.5.0",
    "powered_by": "Nabees Tech Labs",
    "copyright": "© 2026-2099 Nabees Tech. All rights reserved.",
    "tagline": "Streaming made simple, fast, and free! 🚀"
}

# ============================================
# CATEGORIES CONFIGURATION
# ============================================
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
    "indian": "3859721901924910512",
    "hot": "997144265920760504"
}

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
    "indian": {"name": "South Indian Movies", "region": "India", "type": "Movies", "flag": "🇮🇳"},
    "hot": {"name": "Hot Movies 2025", "region": "Global", "type": "Movies", "flag": "🔥"}
}

# ============================================
# API URLs
# ============================================
PLAY_URL = "https://123movienow.cc/wefeed-h5api-bff/subject/play"
CAPTION_URL = "https://h5-api.aoneroom.com/wefeed-h5api-bff/subject/caption"
DETAIL_REC_URL = "https://h5-api.aoneroom.com/wefeed-h5api-bff/subject/detail-rec"
DETAIL_URL = "https://h5-api.aoneroom.com/wefeed-h5api-bff/detail"
SEARCH_URL = "https://vid.davidxtech.de/api/search"

# Headers for category API requests
def get_category_headers():
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Client-Info": '{"timezone":"Africa/Lagos"}',
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjQ2ODM2NjU2ODU2NTc1ODQwMCwiYXRwIjozLCJleHQiOiIxNzcxNDE0NjY0IiwiZXhwIjoxNzc5MTkwNjY0LCJpYXQiOjE3NzE0MTQzNjR9.o6K7hQd3ii0dW-FvuoJ4JMwjTJfOvvlE6G-MTjUV73Y",
        "X-Request-Lang": "en"
    }

# Headers for search API (vid.davidxtech.de)
def get_search_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://vid.davidxtech.de/",
        "Origin": "https://vid.davidxtech.de",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache"
    }

# Headers for streaming
STREAM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://123movienow.cc/",
    "Origin": "https://123movienow.cc"
}

COOKIES = {
    "_ga": "GA1.1.463955875.1771311637",
    "_ga_5W8GT0FPB7": "GS2.1.s1774715648$o7$g1$t1774715738$j60$l0$h0",
    "uuid": "74b149c1-921f-4337-a1a6-8e5122427c7a",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

def add_branding(data):
    """Add branding wrapper to any response"""
    branded_response = OrderedDict()
    branded_response["branding"] = OrderedDict([
        ("creator", BRANDING["creator"]),
        ("api_name", BRANDING["api_name"]),
        ("api_version", BRANDING["api_version"]),
        ("website", BRANDING["website"]),
        ("whatsapp_channel", BRANDING["whatsapp_channel"]),
        ("telegram", BRANDING["telegram"]),
        ("support_email", BRANDING["support_email"]),
        ("tagline", BRANDING["tagline"]),
        ("powered_by", BRANDING["powered_by"])
    ])
    branded_response["data"] = data
    branded_response["status"] = BRANDING["status"]
    branded_response["success"] = BRANDING["success"]
    return branded_response

def get_base_url():
    """Get the base URL of the current request"""
    if request.host.startswith('localhost') or request.host.startswith('127.0.0.1'):
        return f"{request.scheme}://{request.host}"
    else:
        return f"{request.scheme}://{request.host}"

def get_headers(detail_path, subject_id, se, ep):
    return {
        "Host": "123movienow.cc",
        "sec-ch-ua-platform": '"Android"',
        "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        "sec-ch-ua-mobile": "?1",
        "x-client-info": '{"timezone":"Africa/Lagos"}',
        "user-agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36",
        "accept": "application/json",
        "origin": "https://123movienow.cc",
        "referer": f"https://123movienow.cc/spa/videoPlayPage/movies/{detail_path}?id={subject_id}&type=/movie/detail&detailSe={se}&detailEp={ep}&lang=en"
    }

def fetch_streams(subject_id, detail_path, se, ep):
    """Fetch streams and subtitles for a specific episode"""
    params = {"subjectId": subject_id, "se": se, "ep": ep, "detailPath": detail_path}
    res = requests.get(PLAY_URL, headers=get_headers(detail_path, subject_id, se, ep), cookies=COOKIES, params=params, timeout=15)
    data = res.json()
    streams_raw = data.get("data", {}).get("streams", [])
    
    base_url = get_base_url()
    
    streams = []
    for s in streams_raw:
        original_url = s["url"]
        stream_url = f"{base_url}/stream?url={requests.utils.quote(original_url)}"
        download_url = f"{base_url}/download?url={requests.utils.quote(original_url)}"
        
        streams.append({
            "quality": f'{s["resolutions"]}p',
            "format": s["format"],
            "size": int(s["size"]),
            "duration": s["duration"],
            "stream_url": stream_url,
            "download_url": download_url,
            "id": s.get("id")
        })
    
    # Get subtitles
    all_subtitles = []
    if streams_raw:
        first_stream = streams_raw[0]
        cap_params = {
            "format": first_stream["format"],
            "id": first_stream["id"],
            "subjectId": subject_id,
            "detailPath": detail_path
        }
        try:
            cap_res = requests.get(CAPTION_URL, params=cap_params, cookies=COOKIES, timeout=10)
            cap_res.raise_for_status()
            cap_data = cap_res.json()
            
            if cap_data and cap_data.get("code") == 0:
                data_obj = cap_data.get("data", {})
                captions = data_obj.get("captions", [])
                
                for caption in captions:
                    if isinstance(caption, dict):
                        original_sub_url = caption.get("url", "")
                        subtitle_url = f"{base_url}/subtitle/download?url={requests.utils.quote(original_sub_url)}" if original_sub_url else ""
                        
                        subtitle_entry = {
                            "language": caption.get("lanName", caption.get("lan", "Unknown")),
                            "language_code": caption.get("lan", "unknown"),
                            "label": caption.get("lanName", f"{caption.get('lan', 'Unknown')} Subtitle"),
                            "download_url": subtitle_url,
                            "format": "srt",
                            "size": caption.get("size", "0")
                        }
                        
                        if subtitle_entry["download_url"]:
                            all_subtitles.append(subtitle_entry)
        except Exception as e:
            print(f"Error fetching subtitles: {e}")
    
    # Remove duplicates based on language code
    unique_subtitles = []
    seen_languages = set()
    for sub in all_subtitles:
        lang_code = sub.get("language_code")
        if lang_code and lang_code not in seen_languages:
            seen_languages.add(lang_code)
            unique_subtitles.append(sub)
    
    return streams, unique_subtitles

def fetch_detail_path(subject_id):
    """Fetch detailPath from detail-rec endpoint using only subjectId"""
    params = {
        "subjectId": subject_id,
        "page": 1,
        "perPage": 10
    }
    
    try:
        response = requests.get(DETAIL_REC_URL, headers=get_category_headers(), params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0 and data.get("data", {}).get("items"):
            items = data["data"]["items"]
            
            # Find the exact item that matches the requested subjectId
            for item in items:
                if str(item.get("subjectId")) == str(subject_id):
                    return {
                        "detailPath": item.get("detailPath"),
                        "subjectType": item.get("subjectType")
                    }
            
            # If no exact match, try to find by checking the first item (for series that work)
            # This is a fallback for cases where the exact match isn't found
            if items:
                print(f"Warning: Exact subjectId {subject_id} not found, using first item: {items[0].get('title')}")
                first_item = items[0]
                return {
                    "detailPath": first_item.get("detailPath"),
                    "subjectType": first_item.get("subjectType")
                }
        
        return None
    except Exception as e:
        print(f"Error fetching detailPath for {subject_id}: {e}")
        return None

def fetch_complete_details(detail_path):
    """Fetch complete details from detail endpoint using detailPath"""
    params = {"detailPath": detail_path}
    
    try:
        response = requests.get(DETAIL_URL, headers=get_category_headers(), params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0 and data.get("data"):
            detail_data = data["data"]
            subject = detail_data.get("subject", {})
            return {
                "subject": subject,
                "stars": detail_data.get("stars", []),
                "resource": detail_data.get("resource", {})
            }
        return None
    except Exception as e:
        print(f"Error fetching complete details for {detail_path}: {e}")
        return None

# ============================================
# PROXY ENDPOINTS
# ============================================
@app.route("/stream", methods=["GET", "HEAD"])
def proxy_stream():
    video_url = request.args.get("url")
    if not video_url:
        return jsonify({"error": "Missing url parameter"}), 400
    try:
        headers = STREAM_HEADERS.copy()
        if "Range" in request.headers:
            headers["Range"] = request.headers["Range"]
        response = requests.get(video_url, headers=headers, cookies=COOKIES, stream=True, timeout=30)
        if response.status_code not in [200, 206]:
            return jsonify({"error": f"Failed to fetch video: {response.status_code}"}), response.status_code
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        return Response(stream_with_context(generate()), status=response.status_code, headers={
            "Content-Type": response.headers.get("Content-Type", "video/mp4"),
            "Content-Length": response.headers.get("Content-Length"),
            "Accept-Ranges": response.headers.get("Accept-Ranges", "bytes"),
            "Content-Range": response.headers.get("Content-Range"),
            "Cache-Control": "public, max-age=3600"
        })
    except Exception as e:
        return jsonify({"error": f"Failed to fetch stream: {str(e)}"}), 500

@app.route("/download", methods=["GET"])
def proxy_download():
    video_url = request.args.get("url")
    if not video_url:
        return jsonify({"error": "Missing url parameter"}), 400
    try:
        response = requests.get(video_url, headers=STREAM_HEADERS, cookies=COOKIES, stream=True, timeout=30)
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch video: {response.status_code}"}), response.status_code
        filename = video_url.split("/")[-1].split("?")[0]
        if not filename.endswith(".mp4"):
            filename = f"{filename}.mp4"
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        return Response(stream_with_context(generate()), status=200, headers={
            "Content-Type": "video/mp4",
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
            "Content-Length": response.headers.get("Content-Length"),
            "Cache-Control": "public, max-age=3600"
        })
    except Exception as e:
        return jsonify({"error": f"Failed to download: {str(e)}"}), 500

@app.route("/subtitle/download", methods=["GET"])
def download_subtitle():
    subtitle_url = request.args.get("url")
    if not subtitle_url:
        return jsonify({"error": "Missing url parameter"}), 400
    try:
        response = requests.get(subtitle_url, headers={"User-Agent": STREAM_HEADERS["User-Agent"], "Accept": "*/*", "Referer": "https://123movienow.cc/"}, cookies=COOKIES, timeout=30)
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch subtitle: {response.status_code}"}), response.status_code
        filename = subtitle_url.split("/")[-1].split("?")[0]
        if not filename.endswith(".srt"):
            filename = f"{filename}.srt"
        return Response(response.content, status=200, headers={
            "Content-Type": "text/plain; charset=utf-8",
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
            "Content-Length": str(len(response.content)),
            "Cache-Control": "public, max-age=3600"
        })
    except Exception as e:
        return jsonify({"error": f"Failed to fetch subtitle: {str(e)}"}), 500

# ============================================
# CATEGORY & GENRE ENDPOINTS
# ============================================
@app.route("/categories", methods=["GET"])
def list_categories():
    """List all available categories with their info"""
    categories_list = []
    for name, cat_id in CATEGORIES.items():
        info = CATEGORY_INFO.get(name, {"name": name, "flag": "🎬", "region": "Various", "type": "Mixed"})
        categories_list.append({
            "key": name,
            "name": info["name"],
            "flag": info["flag"],
            "id": cat_id,
            "region": info.get("region", "Unknown"),
            "type": info.get("type", "Unknown"),
            "endpoint": f"/movies/{name}"
        })
    return app.response_class(
        response=json.dumps(add_branding({"count": len(categories_list), "categories": categories_list}), ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )

@app.route("/movies/<category>", methods=["GET"])
def get_movies_by_category(category):
    """Get movies/series by category"""
    if category not in CATEGORIES:
        error_response = {"error": "Category not found", "available_categories": list(CATEGORIES.keys())}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )
    
    category_id = CATEGORIES[category]
    page = request.args.get("page", 1)
    per_page = request.args.get("perPage", 12)
    
    try:
        page = int(page)
        per_page = int(per_page)
        if per_page > 50:
            per_page = 50
    except ValueError:
        error_response = {"error": "Invalid page value"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=400,
            mimetype='application/json'
        )
    
    url = f"https://h5-api.aoneroom.com/wefeed-h5api-bff/ranking-list/content?id={category_id}&page={page}&perPage={per_page}"
    
    try:
        response = requests.get(url, headers=get_category_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != 0:
            error_response = {"error": "API error"}
            return app.response_class(
                response=json.dumps(add_branding(error_response), ensure_ascii=False),
                status=500,
                mimetype='application/json'
            )
        
        category_info = CATEGORY_INFO.get(category, {"name": category, "flag": "🎬"})
        result_data = {
            "category": category,
            "category_info": category_info,
            "page": page,
            "content": data.get("data", {})
        }
        
        return app.response_class(
            response=json.dumps(add_branding(result_data), ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        error_response = {"error": str(e)}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=500,
            mimetype='application/json'
        )

@app.route("/genre/<genre_name>", methods=["GET"])
def get_by_genre(genre_name):
    """Get movies/series by genre (horror, war, thriller, comedy, scifi, romance, family)"""
    genre_map = {
        "horror": "Horror", "war": "War", "thriller": "Thriller",
        "comedy": "Comedy", "scifi": "Sci-Fi", "romance": "Romance", "family": "Family"
    }
    genre_flags = {"horror": "👻", "war": "⚔️", "thriller": "🔪", "comedy": "😂", "scifi": "🚀", "romance": "❤️", "family": "👪"}
    
    if genre_name not in genre_map:
        error_response = {"error": f"Genre '{genre_name}' not supported", "available_genres": list(genre_map.keys())}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )
    
    genre = genre_map[genre_name]
    page = request.args.get("page", 1)
    per_page = request.args.get("perPage", 28)
    
    try:
        page = int(page)
        per_page = int(per_page)
        if per_page > 50:
            per_page = 50
    except ValueError:
        error_response = {"error": "Invalid page value"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=400,
            mimetype='application/json'
        )
    
    url = "https://h5-api.aoneroom.com/wefeed-h5api-bff/subject/filter"
    payload = {"page": page, "perPage": per_page, "channelId": 2, "genre": genre}
    
    try:
        response = requests.post(url, json=payload, headers=get_category_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") != 0:
            error_response = {"error": "API error"}
            return app.response_class(
                response=json.dumps(add_branding(error_response), ensure_ascii=False),
                status=500,
                mimetype='application/json'
            )
        
        result_data = {
            "genre": genre_name,
            "genre_info": {"name": genre, "flag": genre_flags.get(genre_name, "🎬")},
            "page": page,
            "content": data.get("data", {})
        }
        
        return app.response_class(
            response=json.dumps(add_branding(result_data), ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        error_response = {"error": str(e)}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=500,
            mimetype='application/json'
        )

# ============================================
# SEARCH ENDPOINT
# ============================================
@app.route("/search", methods=["GET"])
def search_movies():
    """Search for movies and series by title"""
    query = request.args.get("q")
    page = request.args.get("page", 1)
    
    if not query:
        error_response = {"error": "Search query (q) is required", "example": "/search?q=avengers&page=1"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=400,
            mimetype='application/json'
        )
    
    try:
        page = int(page)
    except ValueError:
        error_response = {"error": "Page must be a number"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=400,
            mimetype='application/json'
        )
    
    url = f"{SEARCH_URL}/{query}/?page={page}"
    
    try:
        response = requests.get(url, headers=get_search_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()
        
        formatted_results = []
        items = data.get("results", {}).get("items", [])
        
        for item in items:
            content_type = "Series" if item.get("subjectType") == 2 else "Movie"
            
            movie_data = {
                "title": item.get("title"),
                "type": content_type,
                "genre": item.get("genre"),
                "release_date": item.get("releaseDate"),
                "country": item.get("countryName"),
                "imdb_rating": item.get("imdbRatingValue"),
                "thumbnail": item.get("thumbnail"),
                "cover": item.get("cover"),
                "detail_path": item.get("detailPath"),
                "subject_id": item.get("subjectId"),
                "description": item.get("descriptionShort") or item.get("description", "")
            }
            
            if movie_data["title"] and movie_data["subject_id"]:
                formatted_results.append(movie_data)
        
        result_data = {
            "query": query,
            "page": page,
            "total_results": len(formatted_results),
            "results": formatted_results
        }
        
        return app.response_class(
            response=json.dumps(add_branding(result_data), ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        error_response = {"error": str(e)}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=500,
            mimetype='application/json'
        )

# ============================================
# DETAILS ENDPOINT - WITH DETAILPATH SUPPORT
# ============================================
@app.route("/details", methods=["GET"])
def get_details():
    """Get complete details by subject ID and optional detailPath"""
    subject_id = request.args.get("subjectId")
    detail_path = request.args.get("detailPath")
    
    if not subject_id:
        error_response = {"error": "Missing subjectId parameter"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=400,
            mimetype='application/json'
        )
    
    # If detailPath is provided, use it directly (RELIABLE METHOD)
    if detail_path:
        print(f"🎬 Using provided detailPath: {detail_path}")
        complete_details = fetch_complete_details(detail_path)
        
        if not complete_details:
            error_response = {"error": "Complete details not found"}
            return app.response_class(
                response=json.dumps(add_branding(error_response), ensure_ascii=False),
                status=404,
                mimetype='application/json'
            )
        
        subject = complete_details.get("subject", {})
        content_type = "series" if subject.get("subjectType") == 2 else "movie"
        
        # Clean up cast
        stars = complete_details.get("stars", [])
        unique_stars = []
        seen_ids = set()
        for star in stars:
            staff_id = star.get("staffId")
            if staff_id and staff_id not in seen_ids:
                seen_ids.add(staff_id)
                unique_stars.append(star)
        
        # Build response
        data = OrderedDict()
        data["type"] = content_type
        data["title"] = subject.get("title")
        data["description"] = subject.get("description")
        data["releaseDate"] = subject.get("releaseDate")
        data["genre"] = subject.get("genre")
        data["country"] = subject.get("countryName")
        data["imdbRating"] = {
            "value": subject.get("imdbRatingValue"),
            "count": subject.get("imdbRatingCount")
        }
        data["availableSubtitles"] = subject.get("subtitles")
        data["hasResource"] = subject.get("hasResource")
        data["cover"] = subject.get("cover")
        data["subjectId"] = subject.get("subjectId")
        data["detailPath"] = subject.get("detailPath")
        data["cast"] = unique_stars
        data["seasons"] = complete_details.get("resource", {}).get("seasons", [])
        data["dubs"] = subject.get("dubs", [])
        data["trailer"] = subject.get("trailer")
        
        return app.response_class(
            response=json.dumps(add_branding(data), ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
    
    # If no detailPath, fetch from detail-rec (works for both movies and series)
    print(f"🔍 No detailPath provided, fetching from detail-rec for: {subject_id}")
    detail_path_info = fetch_detail_path(subject_id)
    
    if not detail_path_info:
        error_response = {"error": "Content not found"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )
    
    detail_path = detail_path_info.get("detailPath")
    subject_type = detail_path_info.get("subjectType", 1)
    
    if not detail_path:
        error_response = {"error": "Detail path not found"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )
    
    complete_details = fetch_complete_details(detail_path)
    if not complete_details:
        error_response = {"error": "Complete details not found"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )
    
    subject = complete_details.get("subject", {})
    content_type = "series" if subject_type == 2 else "movie"
    
    stars = complete_details.get("stars", [])
    unique_stars = []
    seen_ids = set()
    for star in stars:
        staff_id = star.get("staffId")
        if staff_id and staff_id not in seen_ids:
            seen_ids.add(staff_id)
            unique_stars.append(star)
    
    data = OrderedDict()
    data["type"] = content_type
    data["title"] = subject.get("title")
    data["description"] = subject.get("description")
    data["releaseDate"] = subject.get("releaseDate")
    data["genre"] = subject.get("genre")
    data["country"] = subject.get("countryName")
    data["imdbRating"] = {
        "value": subject.get("imdbRatingValue"),
        "count": subject.get("imdbRatingCount")
    }
    data["availableSubtitles"] = subject.get("subtitles")
    data["hasResource"] = subject.get("hasResource")
    data["cover"] = subject.get("cover")
    data["subjectId"] = subject.get("subjectId")
    data["detailPath"] = subject.get("detailPath")
    data["cast"] = unique_stars
    data["seasons"] = complete_details.get("resource", {}).get("seasons", [])
    data["dubs"] = subject.get("dubs", [])
    data["trailer"] = subject.get("trailer")
    
    return app.response_class(
        response=json.dumps(add_branding(data), ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )

# ============================================
# STREAMS ENDPOINTS
# ============================================
@app.route("/movie/streams", methods=["GET"])
def movie_streams():
    """Get movie streams using only subjectId"""
    subject_id = request.args.get("subjectId")
    
    if not subject_id:
        error_response = {"error": "Missing subjectId parameter"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=400,
            mimetype='application/json'
        )
    
    # First try to get detailPath from detail-rec
    detail_path_info = fetch_detail_path(subject_id)
    if not detail_path_info:
        error_response = {"error": "Movie not found"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )
    
    detail_path = detail_path_info.get("detailPath")
    if not detail_path:
        error_response = {"error": "Detail path not found"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )
    
    streams, subtitles = fetch_streams(subject_id, detail_path, "0", "0")
    
    data = OrderedDict()
    data["type"] = "movie"
    data["subjectId"] = subject_id
    data["streams"] = streams
    data["subtitles"] = {"available": len(subtitles) > 0, "count": len(subtitles), "list": subtitles}
    
    return app.response_class(
        response=json.dumps(add_branding(data), ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )

@app.route("/series/streams", methods=["GET"])
def series_streams():
    """Get series episode streams using only subjectId"""
    subject_id = request.args.get("subjectId")
    se = request.args.get("se")
    ep = request.args.get("ep")
    
    if not subject_id:
        error_response = {"error": "Missing subjectId parameter"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=400,
            mimetype='application/json'
        )
    
    if se is None or ep is None:
        error_response = {"error": "Missing se (season) or ep (episode) parameters"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=400,
            mimetype='application/json'
        )
    
    # First try to get detailPath from detail-rec
    detail_path_info = fetch_detail_path(subject_id)
    if not detail_path_info:
        error_response = {"error": "Series not found"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )
    
    detail_path = detail_path_info.get("detailPath")
    if not detail_path:
        error_response = {"error": "Detail path not found"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )
    
    streams, subtitles = fetch_streams(subject_id, detail_path, se, ep)
    
    data = OrderedDict()
    data["type"] = "series"
    data["subjectId"] = subject_id
    data["season"] = se
    data["episode"] = ep
    data["streams"] = streams
    data["subtitles"] = {"available": len(subtitles) > 0, "count": len(subtitles), "list": subtitles}
    
    return app.response_class(
        response=json.dumps(add_branding(data), ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )

# ============================================
# HOME & INFO ENDPOINTS
# ============================================
@app.route("/", methods=["GET"])
def home():
    branding_info = OrderedDict()
    branding_info["api_name"] = BRANDING["api_name"]
    branding_info["api_version"] = BRANDING["api_version"]
    branding_info["creator"] = BRANDING["creator"]
    branding_info["tagline"] = BRANDING["tagline"]
    branding_info["website"] = BRANDING["website"]
    branding_info["whatsapp_channel"] = BRANDING["whatsapp_channel"]
    branding_info["telegram"] = BRANDING["telegram"]
    branding_info["support_email"] = BRANDING["support_email"]
    branding_info["powered_by"] = BRANDING["powered_by"]
    branding_info["copyright"] = BRANDING["copyright"]
    branding_info["total_categories"] = len(CATEGORIES)
    branding_info["endpoints"] = {
        "categories": "GET /categories - List all categories",
        "movies": "GET /movies/{category}?page=1&perPage=12 - Get movies by category",
        "genre": "GET /genre/{genre}?page=1&perPage=28 - Filter by genre",
        "search": "GET /search?q={query}&page=1 - Search movies and series",
        "details": "GET /details?subjectId={id}&detailPath={path} - Get details (detailPath optional)",
        "movie_streams": "GET /movie/streams?subjectId={id} - Get movie streams",
        "series_streams": "GET /series/streams?subjectId={id}&se={season}&ep={episode} - Get series streams",
        "stream": "GET /stream?url={url} - Video playback proxy",
        "download": "GET /download?url={url} - Video download proxy",
        "subtitle": "GET /subtitle/download?url={url} - Subtitle download"
    }
    
    return app.response_class(
        response=json.dumps(branding_info, ensure_ascii=False, indent=2),
        status=200,
        mimetype='application/json'
    )

@app.route("/health", methods=["GET"])
def health():
    return app.response_class(
        response=json.dumps({"status": "healthy", "timestamp": time.time()}, ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 70)
    print("🎬 NABEES MOVIE API - COMPLETE EDITION v2.5")
    print("=" * 70)
    print(f"👤 Creator: {BRANDING['creator']}")
    print(f"📱 WhatsApp: {BRANDING['whatsapp_channel']}")
    print(f"🌐 Website: {BRANDING['website']}")
    print(f"📡 Port: {port}")
    print(f"🎯 Total Categories: {len(CATEGORIES)}")
    print("=" * 70)
    print("🚀 ALL ENDPOINTS WORKING:")
    print("   ✅ Categories, Movies, Genre, Search")
    print("   ✅ Details (with optional detailPath)")
    print("   ✅ Movie Streams")
    print("   ✅ Series Streams")
    print("   ✅ Stream/Download/Subtitle Proxies")
    print("=" * 70)
    print("🚀 Server starting on port", port)
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=port, debug=False)
