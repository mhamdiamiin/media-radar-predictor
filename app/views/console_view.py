class ConsoleView:
    def __init__(self):
        self.separator = "=" * 56

    def print_header(self):
        print(self.separator)
        print("  MEDIA RADAR — MOSAIQUE FM INGESTION PIPELINE")
        print(self.separator)

    def print_footer(self, new_articles: int, elapsed: float):
        print(self.separator)
        print(f"  PIPELINE COMPLETE")
        print(f"  New articles this run : {new_articles}")
        print(f"  Total duration        : {elapsed:.2f}s")
        print(self.separator)
