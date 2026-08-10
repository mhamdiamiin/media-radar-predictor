from dotenv import load_dotenv
import os

# Make sure .env is found regardless of where this script is run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

import time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor

from app.controllers.scout_controller import ScoutController
from app.controllers.sweeper_controller import SweeperController
from app.controllers.nlp_controller import run_nlp_pipeline
from app.controllers.clustering_controller import run_clustering_pipeline
from app.controllers.scoring_controller import run_scoring_pipeline
from app.controllers.alert_controller import run_alert_pipeline
from app.views.console_view import ConsoleView


def run_pipeline():
    view = ConsoleView()
    scout = ScoutController()
    sweeper = SweeperController()

    view.print_header()

    start = time.time()

    try:
        new_articles = scout.run()
        sweeper.run()

        print("\n=== Phase 3: NLP Pipeline ===")
        run_nlp_pipeline()

        print("\n=== Phase 4: Clustering ===")
        run_clustering_pipeline()

        print("\n=== Phase 5: Scoring ===")
        run_scoring_pipeline()

        print("\n=== Phase 6: Alerts ===")
        run_alert_pipeline()

        elapsed = time.time() - start
        view.print_footer(new_articles, elapsed)

    except Exception as e:
        print(f"[ERROR] Pipeline run failed: {e}")


def main():
    # max_instances=1 prevents overlapping runs if one takes longer than the interval
    scheduler = BlockingScheduler(
        executors={"default": ThreadPoolExecutor(1)},
        job_defaults={"max_instances": 1, "coalesce": True},
    )

    # Every 2 minutes, 8:00am - 9:58am
    scheduler.add_job(
        run_pipeline,
        CronTrigger(hour="8-9", minute="*/2"),
        id="pipeline_fast",
        name="Pipeline every 2min (8-10am)",
    )

    # Every 5 minutes, rest of the day (00:00-07:59 and 10:00-23:59)
    scheduler.add_job(
        run_pipeline,
        CronTrigger(hour="0-7,10-23", minute="*/5"),
        id="pipeline_slow",
        name="Pipeline every 5min (rest of day)",
    )

    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")


if __name__ == "__main__":
    main()