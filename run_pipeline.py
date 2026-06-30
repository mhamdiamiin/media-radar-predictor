import time
from app.controllers.scout_controller import ScoutController
from app.controllers.sweeper_controller import SweeperController
from app.controllers.nlp_controller import run_nlp_pipeline
from app.controllers.clustering_controller import run_clustering_pipeline
from app.views.console_view import ConsoleView


def main():
    view = ConsoleView()
    scout = ScoutController()
    sweeper = SweeperController()

    view.print_header()

    start = time.time()

    new_articles = scout.run()
    sweeper.run()

    print("\n=== Phase 3: NLP Pipeline ===")
    run_nlp_pipeline()

    print("\n=== Phase 4: Clustering ===")
    run_clustering_pipeline()

    elapsed = time.time() - start

    view.print_footer(new_articles, elapsed)


if __name__ == "__main__":
    main()