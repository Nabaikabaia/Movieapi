from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from collections import OrderedDict
import requests
import json
import os
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ============================================
# ALL CONFIGURATION FROM ENVIRONMENT VARIABLES
# ============================================

# API Configuration
API_TOKEN = os.environ.get("API_TOKEN", "")
COOKIE_TOKEN = os.environ.get("COOKIE_TOKEN", "")
PORT = int(os.environ.get("PORT", 5000))
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# API URLs
PLAY_URL = os.environ.get("PLAY_URL", "https://123movienow.cc/wefeed-h5api-bff/subject/play")
CAPTION_URL = os.environ.get("CAPTION_URL", "https://h5-api.aoneroom.com/wefeed-h5api-bff/subject/caption")
DETAIL_REC_URL = os.environ.get("DETAIL_REC_URL", "https://h5-api.aoneroom.com/wefeed-h5api-bff/subject/detail-rec")
DETAIL_URL = os.environ.get("DETAIL_URL", "https://h5-api.aoneroom.com/wefeed-h5api-bff/detail")
SEARCH_URL = os.environ.get("SEARCH_URL", "https://vid.davidxtech.de/api/search")
POPULAR_SEARCH_URL = os.environ.get("POPULAR_SEARCH_URL", "https://h5-api.aoneroom.com/wefeed-h5api-bff/subject/everyone-search")
SEARCH_SUGGEST_URL = os.environ.get("SEARCH_SUGGEST_URL", "https://h5-api.aoneroom.com/wefeed-h5api-bff/subject/search-suggest")

# ============================================
# BRANDING FROM ENV
# ============================================
BRANDING = {
    "status": 200,
    "success": True,
    "creator": os.environ.get("BRANDING_CREATOR", "Nabees Tech"),
    "developer": os.environ.get("BRANDING_DEVELOPER", "Nabees"),
    "whatsapp_channel": os.environ.get("BRANDING_WHATSAPP", "https://whatsapp.com/channel/0029VawtjOXJpe8X3j3NCZ3j"),
    "website": os.environ.get("BRANDING_WEBSITE", "https://nabees.online"),
    "telegram": os.environ.get("BRANDING_TELEGRAM", "https://t.me/nabeestech"),
    "github": os.environ.get("BRANDING_GITHUB", "https://github.com/Nabaikabaia"),
    "support_email": os.environ.get("BRANDING_EMAIL", "nabees.dev@gmail.com"),
    "api_name": os.environ.get("BRANDING_API_NAME", "Nabees Movie API"),
    "api_version": os.environ.get("BRANDING_VERSION", "3.2.0"),
    "powered_by": os.environ.get("BRANDING_POWERED_BY", "Nabees Tech Labs"),
    "copyright": os.environ.get("BRANDING_COPYRIGHT", "© 2026-2099 Nabees Tech. All rights reserved."),
    "tagline": os.environ.get("BRANDING_TAGLINE", "Streaming made simple, fast, and free! 🚀")
}

# ============================================
# CATEGORIES FROM ENV
# ============================================
CATEGORIES = {
    "anime": os.environ.get("CAT_ANIME", "62133389738001440"),
    "nollywood": os.environ.get("CAT_NOLLYWOOD", "8216283712045280"),
    "black-drama": os.environ.get("CAT_BLACK_DRAMA", "8505361996374835640"),
    "k-drama": os.environ.get("CAT_K_DRAMA", "4380734070238626200"),
    "sa-drama": os.environ.get("CAT_SA_DRAMA", "4307848214843217008"),
    "animation": os.environ.get("CAT_ANIMATION", "7132534597631837112"),
    "bollywood": os.environ.get("CAT_BOLLYWOOD", "414907768299210008"),
    "c-drama": os.environ.get("CAT_C_DRAMA", "173752404280836544"),
    "thai-drama": os.environ.get("CAT_THAI_DRAMA", "1164329479448281992"),
    "returning-tv": os.environ.get("CAT_RETURNING_TV", "8109661952110199232"),
    "top-list": os.environ.get("CAT_TOP_LIST", "1232643093049001320"),
    "new-tv": os.environ.get("CAT_NEW_TV", "2529702013798074864"),
    "popular": os.environ.get("CAT_POPULAR", "997144265920760504"),
    "showmax": os.environ.get("CAT_SHOWMAX", "2076266324048625696"),
    "turkish": os.environ.get("CAT_TURKISH", "9193088611682599936"),
    "indian": os.environ.get("CAT_INDIAN", "3859721901924910512"),
    "hot": os.environ.get("CAT_HOT", "997144265920760504")
}

# Category Metadata
CATEGORY_INFO = {
    "anime": {"name": os.environ.get("INFO_ANIME_NAME", "Anime"), "region": os.environ.get("INFO_ANIME_REGION", "Japan"), "type": os.environ.get("INFO_ANIME_TYPE", "Animation"), "flag": os.environ.get("INFO_ANIME_FLAG", "🇯🇵")},
    "nollywood": {"name": os.environ.get("INFO_NOLLYWOOD_NAME", "Nollywood"), "region": os.environ.get("INFO_NOLLYWOOD_REGION", "Nigeria"), "type": os.environ.get("INFO_NOLLYWOOD_TYPE", "Movies"), "flag": os.environ.get("INFO_NOLLYWOOD_FLAG", "🇳🇬")},
    "black-drama": {"name": os.environ.get("INFO_BLACK_DRAMA_NAME", "Black Drama"), "region": os.environ.get("INFO_BLACK_DRAMA_REGION", "USA/UK"), "type": os.environ.get("INFO_BLACK_DRAMA_TYPE", "TV Series"), "flag": os.environ.get("INFO_BLACK_DRAMA_FLAG", "🎭")},
    "k-drama": {"name": os.environ.get("INFO_K_DRAMA_NAME", "K-Drama"), "region": os.environ.get("INFO_K_DRAMA_REGION", "South Korea"), "type": os.environ.get("INFO_K_DRAMA_TYPE", "TV Series"), "flag": os.environ.get("INFO_K_DRAMA_FLAG", "🇰🇷")},
    "sa-drama": {"name": os.environ.get("INFO_SA_DRAMA_NAME", "South African Drama"), "region": os.environ.get("INFO_SA_DRAMA_REGION", "South Africa"), "type": os.environ.get("INFO_SA_DRAMA_TYPE", "TV Series"), "flag": os.environ.get("INFO_SA_DRAMA_FLAG", "🇿🇦")},
    "animation": {"name": os.environ.get("INFO_ANIMATION_NAME", "Animation"), "region": os.environ.get("INFO_ANIMATION_REGION", "Various"), "type": os.environ.get("INFO_ANIMATION_TYPE", "Animated"), "flag": os.environ.get("INFO_ANIMATION_FLAG", "🎨")},
    "bollywood": {"name": os.environ.get("INFO_BOLLYWOOD_NAME", "Bollywood"), "region": os.environ.get("INFO_BOLLYWOOD_REGION", "India"), "type": os.environ.get("INFO_BOLLYWOOD_TYPE", "Movies"), "flag": os.environ.get("INFO_BOLLYWOOD_FLAG", "🇮🇳")},
    "c-drama": {"name": os.environ.get("INFO_C_DRAMA_NAME", "C-Drama"), "region": os.environ.get("INFO_C_DRAMA_REGION", "China"), "type": os.environ.get("INFO_C_DRAMA_TYPE", "TV Series"), "flag": os.environ.get("INFO_C_DRAMA_FLAG", "🇨🇳")},
    "thai-drama": {"name": os.environ.get("INFO_THAI_DRAMA_NAME", "Thai Drama"), "region": os.environ.get("INFO_THAI_DRAMA_REGION", "Thailand"), "type": os.environ.get("INFO_THAI_DRAMA_TYPE", "TV Series"), "flag": os.environ.get("INFO_THAI_DRAMA_FLAG", "🇹🇭")},
    "returning-tv": {"name": os.environ.get("INFO_RETURNING_TV_NAME", "Returning TV Shows"), "region": os.environ.get("INFO_RETURNING_TV_REGION", "Various"), "type": os.environ.get("INFO_RETURNING_TV_TYPE", "TV Series"), "flag": os.environ.get("INFO_RETURNING_TV_FLAG", "📺")},
    "top-list": {"name": os.environ.get("INFO_TOP_LIST_NAME", "Top Trending"), "region": os.environ.get("INFO_TOP_LIST_REGION", "Global"), "type": os.environ.get("INFO_TOP_LIST_TYPE", "Mixed"), "flag": os.environ.get("INFO_TOP_LIST_FLAG", "🔥")},
    "new-tv": {"name": os.environ.get("INFO_NEW_TV_NAME", "New TV Shows"), "region": os.environ.get("INFO_NEW_TV_REGION", "Various"), "type": os.environ.get("INFO_NEW_TV_TYPE", "TV Series"), "flag": os.environ.get("INFO_NEW_TV_FLAG", "🆕")},
    "popular": {"name": os.environ.get("INFO_POPULAR_NAME", "Popular Movies 2025"), "region": os.environ.get("INFO_POPULAR_REGION", "Various"), "type": os.environ.get("INFO_POPULAR_TYPE", "Movies"), "flag": os.environ.get("INFO_POPULAR_FLAG", "⭐")},
    "showmax": {"name": os.environ.get("INFO_SHOWMAX_NAME", "Showmax Originals"), "region": os.environ.get("INFO_SHOWMAX_REGION", "Africa"), "type": os.environ.get("INFO_SHOWMAX_TYPE", "Originals"), "flag": os.environ.get("INFO_SHOWMAX_FLAG", "📱")},
    "turkish": {"name": os.environ.get("INFO_TURKISH_NAME", "Turkish Drama"), "region": os.environ.get("INFO_TURKISH_REGION", "Turkey"), "type": os.environ.get("INFO_TURKISH_TYPE", "TV Series"), "flag": os.environ.get("INFO_TURKISH_FLAG", "🇹🇷")},
    "indian": {"name": os.environ.get("INFO_INDIAN_NAME", "South Indian Movies"), "region": os.environ.get("INFO_INDIAN_REGION", "India"), "type": os.environ.get("INFO_INDIAN_TYPE", "Movies"), "flag": os.environ.get("INFO_INDIAN_FLAG", "🇮🇳")},
    "hot": {"name": os.environ.get("INFO_HOT_NAME", "Hot Movies 2025"), "region": os.environ.get("INFO_HOT_REGION", "Global"), "type": os.environ.get("INFO_HOT_TYPE", "Movies"), "flag": os.environ.get("INFO_HOT_FLAG", "🔥")}
}

# ============================================
# COOKIES FROM ENV
# ============================================
COOKIES = {
    "_ga": os.environ.get("COOKIE_GA", "GA1.1.463955875.1771311637"),
    "_ga_5W8GT0FPB7": os.environ.get("COOKIE_GA2", "GS2.1.s1774715648$o7$g1$t1774715738$j60$l0$h0"),
    "uuid": os.environ.get("COOKIE_UUID", "74b149c1-921f-4337-a1a6-8e5122427c7a"),
    "token": COOKIE_TOKEN
}

# ============================================
# HEADERS FOR STREAMING
# ============================================
STREAM_HEADERS = {
    "User-Agent": os.environ.get("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
    "Accept": "*/*",
    "Accept-Language": os.environ.get("ACCEPT_LANGUAGE", "en-US,en;q=0.9"),
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": os.environ.get("REFERER", "https://123movienow.cc/"),
    "Origin": os.environ.get("ORIGIN", "https://123movienow.cc"),
    "Sec-Fetch-Dest": "video",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_category_headers():
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Client-Info": os.environ.get("X_CLIENT_INFO", '{"timezone":"Africa/Lagos"}'),
        "Authorization": API_TOKEN,
        "X-Request-Lang": os.environ.get("X_REQUEST_LANG", "en")
    }

def get_search_headers():
    return {
        "User-Agent": STREAM_HEADERS["User-Agent"],
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": STREAM_HEADERS["Accept-Language"],
        "Referer": os.environ.get("SEARCH_REFERER", "https://vid.davidxtech.de/"),
        "Origin": os.environ.get("SEARCH_ORIGIN", "https://vid.davidxtech.de"),
        "Connection": "keep-alive",
        "Cache-Control": "no-cache"
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
        "user-agent": STREAM_HEADERS["User-Agent"],
        "accept": "application/json",
        "origin": "https://123movienow.cc",
        "referer": f"https://123movienow.cc/spa/videoPlayPage/movies/{detail_path}?id={subject_id}&type=/movie/detail&detailSe={se}&detailEp={ep}&lang=en"
    }

def fetch_streams(subject_id, detail_path, se, ep):
    """Fetch streams and subtitles for a specific episode"""
    params = {"subjectId": subject_id, "se": se, "ep": ep, "detailPath": detail_path}
    
    # Create a session with custom headers
    session = requests.Session()
    
    try:
        res = session.get(PLAY_URL, headers=get_headers(detail_path, subject_id, se, ep), cookies=COOKIES, params=params, timeout=30)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        logger.error(f"Error fetching streams: {e}")
        return [], []
    
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
            cap_res = session.get(CAPTION_URL, params=cap_params, cookies=COOKIES, timeout=10)
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
            logger.error(f"Error fetching subtitles: {e}")
    
    # Remove duplicates based on language code
    unique_subtitles = []
    seen_languages = set()
    for sub in all_subtitles:
        lang_code = sub.get("language_code")
        if lang_code and lang_code not in seen_languages:
            seen_languages.add(lang_code)
            unique_subtitles.append(sub)
    
    session.close()
    return streams, unique_subtitles

def fetch_detail_path(subject_id):
    """Fetch detailPath from detail-rec endpoint using only subjectId (fallback)"""
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
            
            for item in items:
                if str(item.get("subjectId")) == str(subject_id):
                    return {
                        "detailPath": item.get("detailPath"),
                        "subjectType": item.get("subjectType"),
                        "title": item.get("title"),
                        "description": item.get("description"),
                        "cover": item.get("cover")
                    }
            
            if items:
                first_item = items[0]
                return {
                    "detailPath": first_item.get("detailPath"),
                    "subjectType": first_item.get("subjectType"),
                    "title": first_item.get("title"),
                    "description": first_item.get("description"),
                    "cover": first_item.get("cover")
                }
        
        return None
    except Exception as e:
        logger.error(f"Error fetching detailPath for {subject_id}: {e}")
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
        logger.error(f"Error fetching complete details for {detail_path}: {e}")
        return None

def fetch_recommendations(subject_id):
    """Fetch you may also like recommendations"""
    params = {
        "subjectId": subject_id,
        "page": 0,
        "perPage": 0
    }
    
    try:
        response = requests.get(DETAIL_REC_URL, headers=get_category_headers(), params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0 and data.get("data", {}).get("items"):
            items = data["data"]["items"]
            recommendations = []
            for item in items:
                if str(item.get("subjectId")) != str(subject_id):
                    recommendations.append({
                        "subjectId": item.get("subjectId"),
                        "title": item.get("title"),
                        "cover": item.get("cover"),
                        "detailPath": item.get("detailPath"),
                        "genre": item.get("genre"),
                        "year": item.get("releaseDate", "").split("-")[0] if item.get("releaseDate") else "",
                        "imdbRating": item.get("imdbRatingValue")
                    })
            return recommendations[:20]
        return []
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}")
        return []

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
        
        # Forward range header for seeking
        if "Range" in request.headers:
            headers["Range"] = request.headers["Range"]
        
        # Remove X-Forwarded-For if present (can cause blocking)
        headers.pop('X-Forwarded-For', None)
        
        response = requests.get(video_url, headers=headers, cookies=COOKIES, stream=True, timeout=30)
        
        if response.status_code not in [200, 206]:
            logger.error(f"Stream failed with status {response.status_code}: {video_url}")
            return jsonify({"error": f"Failed to fetch video: {response.status_code}"}), response.status_code
        
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            stream_with_context(generate()),
            status=response.status_code,
            headers={
                "Content-Type": response.headers.get("Content-Type", "video/mp4"),
                "Content-Length": response.headers.get("Content-Length"),
                "Accept-Ranges": response.headers.get("Accept-Ranges", "bytes"),
                "Content-Range": response.headers.get("Content-Range"),
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Expose-Headers": "Content-Range, Accept-Ranges, Content-Length"
            }
        )
    except Exception as e:
        logger.error(f"Stream proxy error: {e}")
        return jsonify({"error": f"Failed to fetch stream: {str(e)}"}), 500

@app.route("/download", methods=["GET"])
def proxy_download():
    video_url = request.args.get("url")
    if not video_url:
        return jsonify({"error": "Missing url parameter"}), 400
    
    try:
        headers = STREAM_HEADERS.copy()
        headers.pop('X-Forwarded-For', None)
        
        response = requests.get(video_url, headers=headers, cookies=COOKIES, stream=True, timeout=30)
        
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch video: {response.status_code}"}), response.status_code
        
        filename = video_url.split("/")[-1].split("?")[0]
        if not filename.endswith(".mp4"):
            filename = f"{filename}.mp4"
        
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            stream_with_context(generate()),
            status=200,
            headers={
                "Content-Type": "video/mp4",
                "Content-Disposition": f"attachment; filename=\"{filename}\"",
                "Content-Length": response.headers.get("Content-Length"),
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({"error": f"Failed to download: {str(e)}"}), 500

@app.route("/subtitle/download", methods=["GET"])
def download_subtitle():
    subtitle_url = request.args.get("url")
    if not subtitle_url:
        return jsonify({"error": "Missing url parameter"}), 400
    
    try:
        headers = {
            "User-Agent": STREAM_HEADERS["User-Agent"],
            "Accept": "*/*",
            "Referer": "https://123movienow.cc/"
        }
        
        response = requests.get(subtitle_url, headers=headers, cookies=COOKIES, timeout=30)
        
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch subtitle: {response.status_code}"}), response.status_code
        
        filename = subtitle_url.split("/")[-1].split("?")[0]
        if not filename.endswith(".srt"):
            filename = f"{filename}.srt"
        
        return Response(
            response.content,
            status=200,
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "Content-Disposition": f"attachment; filename=\"{filename}\"",
                "Content-Length": str(len(response.content)),
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*"
            }
        )
    except Exception as e:
        logger.error(f"Subtitle download error: {e}")
        return jsonify({"error": f"Failed to fetch subtitle: {str(e)}"}), 500

# ============================================
# CATEGORY & GENRE ENDPOINTS
# ============================================
@app.route("/categories", methods=["GET"])
def list_categories():
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
        logger.error(f"Movies by category error: {e}")
        error_response = {"error": str(e)}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=500,
            mimetype='application/json'
        )

@app.route("/genre/<genre_name>", methods=["GET"])
def get_by_genre(genre_name):
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
        logger.error(f"Genre filter error: {e}")
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
        logger.error(f"Search error: {e}")
        error_response = {"error": str(e)}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=500,
            mimetype='application/json'
        )

# ============================================
# POPULAR SEARCHES ENDPOINT
# ============================================
@app.route("/popular-searches", methods=["GET"])
def popular_searches():
    try:
        response = requests.get(POPULAR_SEARCH_URL, headers=get_category_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0 and data.get("data", {}).get("everyoneSearch"):
            popular = data["data"]["everyoneSearch"]
            result_data = {"popular_searches": popular}
            return app.response_class(
                response=json.dumps(add_branding(result_data), ensure_ascii=False),
                status=200,
                mimetype='application/json'
            )
        else:
            error_response = {"error": "Failed to fetch popular searches"}
            return app.response_class(
                response=json.dumps(add_branding(error_response), ensure_ascii=False),
                status=500,
                mimetype='application/json'
            )
    except Exception as e:
        logger.error(f"Popular searches error: {e}")
        error_response = {"error": str(e)}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=500,
            mimetype='application/json'
        )

# ============================================
# SEARCH SUGGEST ENDPOINT
# ============================================
@app.route("/search-suggest", methods=["POST"])
def search_suggest():
    try:
        request_data = request.get_json()
        if not request_data:
            error_response = {"error": "Request body is required"}
            return app.response_class(
                response=json.dumps(add_branding(error_response), ensure_ascii=False),
                status=400,
                mimetype='application/json'
            )
        
        keyword = request_data.get("keyword")
        per_page = request_data.get("perPage", 10)
        
        if not keyword:
            error_response = {"error": "keyword is required"}
            return app.response_class(
                response=json.dumps(add_branding(error_response), ensure_ascii=False),
                status=400,
                mimetype='application/json'
            )
        
        payload = {"keyword": keyword, "perPage": per_page}
        response = requests.post(SEARCH_SUGGEST_URL, json=payload, headers=get_category_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == 0 and data.get("data", {}).get("items"):
            result_data = {
                "keyword": data["data"].get("keyword", keyword),
                "suggestions": data["data"]["items"]
            }
            return app.response_class(
                response=json.dumps(add_branding(result_data), ensure_ascii=False),
                status=200,
                mimetype='application/json'
            )
        else:
            error_response = {"error": "Failed to fetch suggestions"}
            return app.response_class(
                response=json.dumps(add_branding(error_response), ensure_ascii=False),
                status=500,
                mimetype='application/json'
            )
    except Exception as e:
        logger.error(f"Search suggest error: {e}")
        error_response = {"error": str(e)}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=500,
            mimetype='application/json'
        )

# ============================================
# DETAILS ENDPOINT
# ============================================
@app.route("/details", methods=["GET"])
def get_details():
    detail_path = request.args.get("detailPath")
    subject_id = request.args.get("subjectId")
    
    if not detail_path and not subject_id:
        error_response = {"error": "Missing detailPath or subjectId parameter"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=400,
            mimetype='application/json'
        )
    
    if not detail_path and subject_id:
        path_info = fetch_detail_path(subject_id)
        if path_info:
            detail_path = path_info.get("detailPath")
        else:
            error_response = {"error": "Could not find detailPath for the given subjectId"}
            return app.response_class(
                response=json.dumps(add_branding(error_response), ensure_ascii=False),
                status=404,
                mimetype='application/json'
            )
    
    if not detail_path:
        error_response = {"error": "Invalid detailPath"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )
    
    complete_details = fetch_complete_details(detail_path)
    if not complete_details:
        error_response = {"error": "Movie/Series not found"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=404,
            mimetype='application/json'
        )
    
    subject = complete_details.get("subject", {})
    actual_subject_id = subject.get("subjectId")
    
    recommendations = []
    if actual_subject_id:
        recommendations = fetch_recommendations(actual_subject_id)
    
    content_type = "series" if subject.get("subjectType") == 2 else "movie"
    
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
    data["you_may_also_like"] = recommendations
    
    return app.response_class(
        response=json.dumps(add_branding(data), ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )

# ============================================
# UNIFIED SOURCES ENDPOINT
# ============================================
@app.route("/sources", methods=["GET"])
def get_sources():
    subject_id = request.args.get("subjectId")
    detail_path = request.args.get("detailPath")
    se = request.args.get("se")
    ep = request.args.get("ep")
    
    if not subject_id:
        error_response = {"error": "Missing subjectId parameter"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=400,
            mimetype='application/json'
        )
    
    if not detail_path:
        error_response = {"error": "Missing detailPath parameter. Use: /sources?subjectId=xxx&detailPath=yyy&se=1&ep=1 (se/ep optional)"}
        return app.response_class(
            response=json.dumps(add_branding(error_response), ensure_ascii=False),
            status=400,
            mimetype='application/json'
        )
    
    # Check if season and episode are provided
    if se is not None and ep is not None:
        # Series episode
        streams, subtitles = fetch_streams(subject_id, detail_path, se, ep)
        
        data = OrderedDict()
        data["type"] = "series"
        data["subjectId"] = subject_id
        data["detailPath"] = detail_path
        data["season"] = se
        data["episode"] = ep
        data["streams"] = streams
        data["subtitles"] = {"available": len(subtitles) > 0, "count": len(subtitles), "list": subtitles}
        
    else:
        # Movie (no season/episode)
        streams, subtitles = fetch_streams(subject_id, detail_path, "0", "0")
        
        data = OrderedDict()
        data["type"] = "movie"
        data["subjectId"] = subject_id
        data["detailPath"] = detail_path
        data["streams"] = streams
        data["subtitles"] = {"available": len(subtitles) > 0, "count": len(subtitles), "list": subtitles}
    
    return app.response_class(
        response=json.dumps(add_branding(data), ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )

# ============================================
# BEAUTIFUL FRAMED HOME PAGE
# ============================================
@app.route("/", methods=["GET"])
def home():
    base_url = get_base_url()
    
    categories_list = list(CATEGORIES.keys())
    categories_display = ' '.join([f"「{cat}」" for cat in categories_list[:10]]) + (' ...' if len(categories_list) > 10 else '')
    genres_display = ' '.join([f"「{g}」" for g in ['horror', 'war', 'thriller', 'comedy', 'scifi', 'romance', 'family']])
    
    content = f"""
╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃                                                                    ┃
┃                         🎬 NABEES MOVIE API                        ┃
┃                            v{BRANDING['api_version']}                            ┃
┃                                                                    ┃
┃                  {BRANDING['tagline']}                  ┃
┃                                                                    ┃
├┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┤
┃                                                                    ┃
┃  👤 Creator      : {BRANDING['creator']:<44}┃
┃  📱 WhatsApp     : {BRANDING['whatsapp_channel']:<44}┃
┃  🌐 Website      : {BRANDING['website']:<44}┃
┃  💬 Telegram     : {BRANDING['telegram']:<44}┃
┃  📧 Support      : {BRANDING['support_email']:<44}┃
┃                                                                    ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃  📂 CATEGORIES                                                     ┃
┃  ─────────────────────────────────────────────────────────────────┃
┃                                                                    ┃
┃  GET  /categories                                                  ┃
┃  GET  /movies/«category»?page=1&perPage=12                         ┃
┃                                                                    ┃
┃  {categories_display}                  ┃
┃                                                                    ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃  🎭 GENRE FILTERS                                                  ┃
┃  ─────────────────────────────────────────────────────────────────┃
┃                                                                    ┃
┃  GET  /genre/«genre»?page=1&perPage=28                             ┃
┃                                                                    ┃
┃  {genres_display}                       ┃
┃                                                                    ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃  🔍 SEARCH                                                         ┃
┃  ─────────────────────────────────────────────────────────────────┃
┃                                                                    ┃
┃  GET  /search?q=«query»&page=1                                     ┃
┃  GET  /popular-searches                                            ┃
┃  POST /search-suggest                                              ┃
┃                                                                    ┃
┃  ┌──────────────────────────────────────────────────────────────┐ ┃
┃  │  Body: {{"keyword": "movie name", "perPage": 10}}           │ ┃
┃  └──────────────────────────────────────────────────────────────┘ ┃
┃                                                                    ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃  🎬 MOVIE / SERIES INFO                                            ┃
┃  ─────────────────────────────────────────────────────────────────┃
┃                                                                    ┃
┃  GET  /details?detailPath=«path»                                   ┃
┃  GET  /details?subjectId=«id»                                      ┃
┃                                                                    ┃
┃  ✨ Returns: Full details + You May Also Like recommendations      ┃
┃                                                                    ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃  📺 STREAMS & DOWNLOADS                                            ┃
┃  ─────────────────────────────────────────────────────────────────┃
┃                                                                    ┃
┃  GET  /sources?subjectId=«id»&detailPath=«path»                   ┃
┃       (For movies - no se/ep)                                     ┃
┃                                                                    ┃
┃  GET  /sources?subjectId=«id»&detailPath=«path»&se=1&ep=1         ┃
┃       (For series episodes)                                       ┃
┃                                                                    ┃
┃  GET  /stream?url=«url»  (Video playback)                         ┃
┃  GET  /download?url=«url»  (Direct download)                      ┃
┃  GET  /subtitle/download?url=«url»  (Subtitle download)           ┃
┃                                                                    ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃  📝 QUICK EXAMPLES                                                 ┃
┃  ─────────────────────────────────────────────────────────────────┃
┃                                                                    ┃
┃  ┌──────────────────────────────────────────────────────────────┐ ┃
┃  │  # Get popular searches                                      │ ┃
┃  │  curl {base_url}/popular-searches                           │ ┃
┃  └──────────────────────────────────────────────────────────────┘ ┃
┃                                                                    ┃
┃  ┌──────────────────────────────────────────────────────────────┐ ┃
┃  │  # Search for movies                                         │ ┃
┃  │  curl "{base_url}/search?q=avengers"                        │ ┃
┃  └──────────────────────────────────────────────────────────────┘ ┃
┃                                                                    ┃
┃  ┌──────────────────────────────────────────────────────────────┐ ┃
┃  │  # Get movie sources                                         │ ┃
┃  │  curl "{base_url}/sources?subjectId=3562334115405909808&detailPath=brave-4YlSeNJw9f4" │ ┃
┃  └──────────────────────────────────────────────────────────────┘ ┃
┃                                                                    ┃
┃  ┌──────────────────────────────────────────────────────────────┐ ┃
┃  │  # Get series episode                                        │ ┃
┃  │  curl "{base_url}/sources?subjectId=4006958073083480920&detailPath=peaky-blinders-Ii0kbUrUZL4&se=1&ep=1" │ ┃
┃  └──────────────────────────────────────────────────────────────┘ ┃
┃                                                                    ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃  ℹ️ INFO                                                           ┃
┃  ─────────────────────────────────────────────────────────────────┃
┃                                                                    ┃
┃  GET  /                                                            ┃
┃  GET  /health                                                      ┃
┃                                                                    ┃
┃  ⚡ Response Format: {{"branding": {{...}}, "data": {{...}}, "status": 200, "success": true}} ┃
┃                                                                    ┃
┃  🔗 Base URL : {base_url:<53}┃
┃  🚀 Status    : ONLINE                                             ┃
┃  ©️ Copyright : {BRANDING['copyright']:<53}┃
┃                                                                    ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
"""
    
    return app.response_class(
        response=content,
        status=200,
        mimetype='text/plain'
    )

@app.route("/health", methods=["GET"])
def health():
    return app.response_class(
        response=json.dumps({"status": "healthy", "timestamp": time.time()}, ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info(f"🎬 {BRANDING['api_name']} - v{BRANDING['api_version']}")
    logger.info("=" * 70)
    logger.info(f"👤 Creator: {BRANDING['creator']}")
    logger.info(f"📱 WhatsApp: {BRANDING['whatsapp_channel']}")
    logger.info(f"🌐 Website: {BRANDING['website']}")
    logger.info(f"📡 Port: {PORT}")
    logger.info("=" * 70)
    logger.info("✅ All configuration loaded from environment variables")
    logger.info("✅ UNIFIED /sources endpoint active")
    logger.info("✅ Movie: /sources?subjectId=xxx&detailPath=yyy")
    logger.info("✅ Series: /sources?subjectId=xxx&detailPath=yyy&se=1&ep=1")
    logger.info("=" * 70)
    
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
