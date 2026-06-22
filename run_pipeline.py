import time

from process_1_scout import run_sitemap_scout
from process_2_sweeper import run_bulk_sweeper


def main():
    print("=" * 56)
    print("  MEDIA RADAR — MOSAIQUE FM INGESTION PIPELINE")
    print("=" * 56)

    start = time.time()
    new_articles = run_sitemap_scout()
    run_bulk_sweeper()

    elapsed = time.time() - start
    print("=" * 56)
    print(f"  PIPELINE COMPLETE")
    print(f"  New articles this run : {new_articles}")
    print(f"  Total duration        : {elapsed:.2f}s")
    print("=" * 56)


if __name__ == "__main__":
    main()