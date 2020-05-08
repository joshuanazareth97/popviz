import sys
import argparse

from scraper import IMDBScraper
from search import search_imdb
from reports import TVReport


def get_results_from_imdb(query):
    results = search_imdb(query)[:10]
    if not results:
        print("No results found! Check the search term.")
        sys.exit(1)
    elif len(results) == 1:
        chosen = results[0]
        print(
            f"Found a single result: {chosen['showname']} ({chosen['year']}) with ID {chosen['id']}"
        )
        input("Continue?")
        print()
    else:
        for num, result in enumerate(results):
            name = result["showname"]
            cat = result["category"]
            date = result["year"]
            print(f"{num+1}. {name}\t({date})\t[{cat}]")
        print()
        while True:
            choice = input("Choose one of the above shows (Or enter 0 to exit) > ")
            try:
                choice = int(choice) - 1
            except ValueError:
                print("Please enter a valid (numerical) choice.\n")
                continue
            if choice == -1:  # User input 0, which gets saved as -1
                print("Exiting app. Bye bye!")
                sys.exit(0)
            try:
                chosen = results[choice]
            except IndexError:
                print("Please enter a number present in the list above.\n")
                continue
            break
        print(f"You have chosen {chosen['showname']} with ID: {chosen['id']}\n")
    return chosen


def main():
    print()
    parser = argparse.ArgumentParser(
        description="Generate beautiful reports of IMDb ratings data."
    )

    input_term_group = parser.add_mutually_exclusive_group()
    input_term_group.add_argument(
        "-s", "--search", help="Search for a television show."
    )
    input_term_group.add_argument(
        "-i", "--id", help="Directly provide the IMDb ID of a television show."
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Specify a filename for the output. Defaults to the name of the show.",
        default=None,
    )

    args = parser.parse_args()
    if not args.id:
        if not args.search:
            query = input("Enter a search term for a television show > ")
            print()
        else:
            query = args.search.strip()
        print(f'Searching for "{query}" on IMDb...')
        chosen = get_results_from_imdb(query)
        chosen_id = chosen["id"]
    else:
        chosen_id = args.id
    print("Retrieving show data...")
    scraper = IMDBScraper(chosen_id)
    reporter = TVReport(data_provider=scraper)
    print("\nGenerating report...")
    reporter.heatmap()
    file = reporter.save_file(output_dir="./data", filename=args.output)
    print(f"Report saved to {file.absolute()}.")


if __name__ == "__main__":
    main()
