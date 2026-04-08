"""Metabolica Daemon - Daily Metabolism Core Loop"""

import logging
import time
import schedule
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("metabolica")


def daily_metabolism():
    """Run the daily metabolism cycle."""
    today = datetime.now(JST).strftime("%Y-%m-%d")
    log.info("=== Daily Metabolism Start: %s ===", today)

    # Phase 1: COLLECT
    log.info("Phase 1: COLLECT - fetching public API data")
    # TODO: implement collect phase

    # Phase 2: DIGEST
    log.info("Phase 2: DIGEST - analyzing collected data")
    # TODO: implement digest phase

    # Phase 3: METABOLIZE
    log.info("Phase 3: METABOLIZE - heavy computation")
    # TODO: implement metabolize phase

    # Phase 4: ENCODE
    log.info("Phase 4: ENCODE - generating DNA sequence")
    # TODO: implement encode phase

    # Phase 5: APPEND
    log.info("Phase 5: APPEND - storing to S3 + DynamoDB")
    # TODO: implement append phase

    log.info("=== Daily Metabolism Complete: %s ===", today)


def main():
    log.info("Metabolica Daemon starting...")

    # Run metabolism daily at 03:00 JST
    schedule.every().day.at("03:00").do(daily_metabolism)

    # Run once on startup if not yet run today
    log.info("Running initial metabolism cycle...")
    daily_metabolism()

    log.info("Scheduler active. Waiting for next cycle...")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
