import json
from pathlib import Path

from scraper import IMDBScraper
from reports import TVReport


def main():
    show_id = "tt0472954"
    show_id = "tt0108778"
    show_id = "tt0367279"
    iasip = IMDBScraper(show_id)
    title = iasip.show_metadata["title"]
    print(f"Retrieved show data for {title} from IMDb.")

    print(iasip.show_metadata)
    reporter = TVReport(data_provider=iasip)

    print("Generating heatmap...")
    reporter.heatmap(output_dir="./data", color="blue")
    iasip.dump()


if __name__ == "__main__":
    print("Welcome to PopViz. Use the -h flag for more options.")
    main()
