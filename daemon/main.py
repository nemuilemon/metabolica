"""Metabolica Daemon - Metabolism Core Loop (every 30 min)"""

import io
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
    upload_log,
)

JST = timezone(timedelta(hours=9))

# Capture logs in memory for S3 upload
log_buffer = io.StringIO()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),           # stdout → journalctl
        logging.StreamHandler(log_buffer),  # memory → S3
    ],
)
log = logging.getLogger("metabolica")


def metabolism_cycle():
    """Run a single metabolism cycle — five phases end-to-end."""
    log_buffer.truncate(0)
    log_buffer.seek(0)

    now = datetime.now(JST)
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    log.info("=== Metabolism Cycle Start: %s ===", timestamp)

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
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
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

    log.info("=== Metabolism Cycle Complete: day %d (%s) ===", day, timestamp)

    # Upload this cycle's log to S3
    try:
        upload_log(log_buffer.getvalue(), day, now)
    except Exception as e:
        log.error("Failed to upload log to S3: %s", e)


def main():
    log.info("Metabolica Daemon starting (30min interval)...")

    # Run every 30 minutes
    schedule.every(30).minutes.do(metabolism_cycle)

    # Run once on startup
    log.info("Running initial metabolism cycle...")
    metabolism_cycle()

    log.info("Scheduler active. Next cycle in 30 minutes...")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
