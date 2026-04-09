"""COLLECT Phase - Fetch data from public APIs (no auth required)"""

import logging
from datetime import datetime, timezone

import requests

log = logging.getLogger("metabolica.collect")

TIMEOUT = 10
USER_AGENT = "metabolica/0.1 (https://github.com/nemuilemon/metabolica)"


def _get(url: str, params: dict | None = None) -> dict | list | None:
    try:
        r = requests.get(
            url,
            params=params,
            timeout=TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.warning("fetch failed: %s (%s)", url, e)
        return None


def fetch_hackernews_top(limit: int = 10) -> list[dict]:
    """HackerNews top stories — tech world pulse."""
    ids = _get("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not ids:
        return []
    stories = []
    for story_id in ids[:limit]:
        item = _get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
        if item:
            stories.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "score": item.get("score"),
                "by": item.get("by"),
                "url": item.get("url"),
            })
    return stories


def fetch_wikipedia_featured() -> dict:
    """Wikipedia today's featured article + on-this-day events."""
    today = datetime.now(timezone.utc).strftime("%Y/%m/%d")
    data = _get(f"https://api.wikimedia.org/feed/v1/wikipedia/en/featured/{today}")
    if not data:
        return {}
    return {
        "featured_article": (data.get("tfa") or {}).get("titles", {}).get("normalized"),
        "most_read_count": len((data.get("mostread") or {}).get("articles", [])),
        "on_this_day_count": len(data.get("onthisday", [])),
        "image_title": (data.get("image") or {}).get("title"),
    }


def fetch_weather_tokyo() -> dict:
    """Open-Meteo — Tokyo weather (no auth)."""
    data = _get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": 35.6762,
            "longitude": 139.6503,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "timezone": "Asia/Tokyo",
        },
    )
    if not data:
        return {}
    return data.get("current", {})


def fetch_earthquakes() -> dict:
    """USGS — significant earthquakes in last 24h."""
    data = _get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_day.geojson")
    if not data:
        return {}
    features = data.get("features", [])
    return {
        "count": len(features),
        "max_magnitude": max(
            (f.get("properties", {}).get("mag") or 0 for f in features),
            default=0,
        ),
    }


def fetch_crypto_market() -> dict:
    """CoinGecko — global crypto market state."""
    data = _get("https://api.coingecko.com/api/v3/global")
    if not data:
        return {}
    market = data.get("data", {})
    return {
        "total_market_cap_usd": market.get("total_market_cap", {}).get("usd"),
        "total_volume_usd": market.get("total_volume", {}).get("usd"),
        "btc_dominance": market.get("market_cap_percentage", {}).get("btc"),
        "active_cryptocurrencies": market.get("active_cryptocurrencies"),
    }


def fetch_iss_position() -> dict:
    """ISS current position — life continues above."""
    data = _get("http://api.open-notify.org/iss-now.json")
    if not data:
        return {}
    return data.get("iss_position", {})


def collect_all() -> dict:
    """Run all collectors and return aggregated data."""
    log.info("Collecting from public APIs...")

    result = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "hackernews": fetch_hackernews_top(),
            "wikipedia": fetch_wikipedia_featured(),
            "weather_tokyo": fetch_weather_tokyo(),
            "earthquakes": fetch_earthquakes(),
            "crypto": fetch_crypto_market(),
            "iss": fetch_iss_position(),
        },
    }

    success_count = sum(1 for v in result["sources"].values() if v)
    log.info("Collected from %d/%d sources", success_count, len(result["sources"]))
    return result
