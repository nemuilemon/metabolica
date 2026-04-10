"""DIGEST Phase - Extract features from raw collected data"""

import hashlib
import json
import logging

log = logging.getLogger("metabolica.digest")


def _extract_texts(collected: dict) -> list[str]:
    texts: list[str] = []
    sources = collected.get("sources", {})

    for story in sources.get("hackernews") or []:
        if title := story.get("title"):
            texts.append(title)

    wiki = sources.get("wikipedia") or {}
    if article := wiki.get("featured_article"):
        texts.append(article)
    if image := wiki.get("image_title"):
        texts.append(image)

    return texts


def _extract_numerics(collected: dict) -> dict:
    sources = collected.get("sources", {})
    weather = sources.get("weather_tokyo") or {}
    crypto = sources.get("crypto") or {}
    earthquakes = sources.get("earthquakes") or {}
    iss = sources.get("iss") or {}

    return {
        "temperature": weather.get("temperature_2m"),
        "humidity": weather.get("relative_humidity_2m"),
        "wind_speed": weather.get("wind_speed_10m"),
        "weather_code": weather.get("weather_code"),
        "btc_dominance": crypto.get("btc_dominance"),
        "market_cap_usd": crypto.get("total_market_cap_usd"),
        "earthquake_count": earthquakes.get("count", 0),
        "earthquake_max_mag": earthquakes.get("max_magnitude", 0),
        "iss_latitude": float(iss.get("latitude", 0) or 0),
        "iss_longitude": float(iss.get("longitude", 0) or 0),
    }


def digest(collected: dict) -> dict:
    """Reduce raw collected data to a deterministic feature bundle + seed."""
    log.info("Digesting collected data...")

    texts = _extract_texts(collected)
    numerics = _extract_numerics(collected)
    full_text = " ".join(texts)

    # Canonical serialization for reproducibility
    canonical = json.dumps(
        {"text": full_text, "numerics": numerics},
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")
    seed = hashlib.sha256(canonical).digest()

    log.info("Digest: %d texts, %d numerics, seed=%s",
             len(texts), len(numerics), seed.hex()[:16])

    return {
        "text_length": len(full_text),
        "text_count": len(texts),
        "numerics": numerics,
        "seed_hex": seed.hex(),
        "raw_hash": hashlib.sha256(canonical).hexdigest(),
    }
