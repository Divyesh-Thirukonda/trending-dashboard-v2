import requests
import json
import time
import yt_dlp
from datetime import datetime, timedelta
from pytrends.request import TrendReq
from bs4 import BeautifulSoup
import random

# --- YouTube ---
def fetch_youtube():
    print("Fetching YouTube...")
    try:
        ydl_opts = {
            'quiet': True, 'extract_flat': True, 'noplaylist': True,
            'force_generic_extractor': False
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # "Trending" search proxy
            info = ydl.extract_info("ytsearch15:trending", download=False)
            videos = []
            if 'entries' in info:
                for entry in info['entries']:
                    videos.append({
                        'title': entry.get('title', 'Unknown'),
                        'channel': entry.get('uploader', 'Unknown'),
                        'views': entry.get('view_count', 0),
                        'url': entry.get('url', f"https://youtube.com/watch?v={entry.get('id')}")
                    })
            return {"source": "youtube", "data": videos}
    except Exception as e:
        print(f"YouTube Error: {e}")
        return None

# --- TikTok ---
def fetch_tiktok():
    print("Fetching TikTok...")
    try:
        url = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        script = soup.find("script", {"id": "__NEXT_DATA__"})
        
        hashtags = []
        if script:
            data = json.loads(script.string)
            state = data['props']['pageProps']['dehydratedState']
            if 'queries' in state:
                for q in state['queries']:
                    if 'state' in q and 'data' in q['state']:
                        d = q['state']['data']
                        target = d.get('pages', [d])[0] if 'pages' in d else d
                        if 'list' in target:
                            for item in target['list'][:10]:
                                if 'hashtagName' in item:
                                    hashtags.append({
                                        "name": item.get('hashtagName'),
                                        "views": item.get('videoViews', 0),
                                        "rank": item.get('rank')
                                    })
        return {"source": "tiktok", "data": hashtags}
    except Exception as e:
        print(f"TikTok Error: {e}")
        return None

# --- Wikipedia ---
def fetch_wikipedia():
    print("Fetching Wikipedia...")
    try:
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y/%m/%d")
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{date_str}"
        headers = {"User-Agent": "TrendingDashboardV2/1.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            items = response.json()['items'][0]['articles']
            articles = []
            seen = set()
            for item in items:
                title = item['article']
                if "Special:" in title or "Main_Page" in title or title in seen: continue
                seen.add(title)
                articles.append({"title": title.replace("_", " "), "views": item['views']})
                if len(articles) >= 10: break
            return {"source": "wikipedia", "data": articles}
    except Exception as e:
        print(f"Wiki Error: {e}")
        return None

# --- Hacker News ---
def fetch_hackernews():
    print("Fetching Hacker News...")
    try:
        ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:10]
        stories = []
        for id in ids:
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json").json()
            stories.append({
                "title": item.get('title'),
                "score": item.get('score'),
                "url": item.get('url', f"https://news.ycombinator.com/item?id={id}")
            })
        return {"source": "hackernews", "data": stories}
    except Exception as e:
        print(f"HN Error: {e}")
        return None

# --- GitHub ---
def fetch_github():
    print("Fetching GitHub...")
    try:
        last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        url = f"https://api.github.com/search/repositories?q=created:>{last_week}&sort=stars&order=desc"
        headers = {"Accept": "application/vnd.github.v3+json"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            repos = []
            for item in response.json()['items'][:10]:
                repos.append({
                    "name": item['full_name'],
                    "stars": item['stargazers_count'],
                    "description": item['description'],
                    "url": item['html_url']
                })
            return {"source": "github", "data": repos}
    except Exception as e:
        print(f"GitHub Error: {e}")
        return None

# --- Google Trends ---
def fetch_google_trends():
    print("Fetching Google Trends...")
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        # We'll fetch a generic list or a specific keyword. 
        # Since V1 was keyword based, let's track a generic "Python" or "AI" for the dashboard background,
        # OR just Trending Searches.
        # Let's do Trending Searches (Realtime)
        df = pytrends.trending_searches(pn='united_states') # returns series
        trends = [{"name": x} for x in df[0].values[:10]]
        return {"source": "google_trends", "data": trends}
    except Exception as e:
        print(f"Google Trends Error: {e}")
        return None

def fetch_all():
    return [
        fetch_youtube(),
        fetch_tiktok(),
        fetch_wikipedia(),
        fetch_hackernews(),
        fetch_github(),
        fetch_google_trends()
    ]
