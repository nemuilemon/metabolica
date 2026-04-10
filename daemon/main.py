"""Metabolica Daemon - Daily Metabolism Core Loop"""

import logging
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import schedule

# Allow importing lib/ from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collect import collect_all  # noqa: E402
from digest import digest  # noqa: E402
from encode import encode_dna  # noqa: E402
from metabolize import metabolize  # noqa: E402
from storage import (  # noqa: E402
    append_dna_chain,
    get_latest_chain_entry,
    save_dna_record,
    save_raw_collection,
)

JST = timezone(timedelta(hours=9))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("metabolica")


def daily_metabolism():
    """Run the daily metabolism cycle — five phases end-to-end."""
    today = datetime.now(JST).strftime("%Y-%m-%d")
    log.info("=== Daily Metabolism Start: %s ===", today)

    # Phase 1: COLLECT
    log.info("Phase 1: COLLECT")
    collected = collect_all()
    try:
        save_raw_collection(collected)
    except Exception as e:
        log.error("Failed to save raw collection to S3: %s", e)

    # Phase 2: DIGEST
    log.info("Phase 2: DIGEST")
    digested = digest(collected)
    seed = bytes.fromhex(digested["seed_hex"])

    # Phase 3: METABOLIZE
    log.info("Phase 3: METABOLIZE")
    metabolism = metabolize(seed)

    # Phase 4: ENCODE
    log.info("Phase 4: ENCODE")
    dna = encode_dna(metabolism)

    # Phase 5: APPEND
    log.info("Phase 5: APPEND")
    prev_day, prev_hash = get_latest_chain_entry()
    day = prev_day + 1

    record = {
        "day": day,
        "date": today,
        "raw_hash": digested["raw_hash"],
        "prev_day_hash": prev_hash,
        "digest_summary": {
            "text_length": digested["text_length"],
            "text_count": digested["text_count"],
            "numerics": digested["numerics"],
        },
        "genes": dna["genes"],
        "metabolism_proof": metabolism["proof"],
        "cellular_automata_state": dna["cellular_automata_state"],
    }

    try:
        save_dna_record(record)
        append_dna_chain(record)
    except Exception as e:
        log.error("Failed to persist DNA record: %s", e)

    log.info("=== Daily Metabolism Complete: day %d (%s) ===", day, today)


def main():
    log.info("Metabolica Daemon starting...")

    # Run metabolism daily at 03:00 JST
    schedule.every().day.at("03:00").do(daily_metabolism)

    # Run once on startup
    log.info("Running initial metabolism cycle...")
    daily_metabolism()

    log.info("Scheduler active. Waiting for next cycle...")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
