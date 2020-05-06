import sys

from scraper import IMDBScraper
from search import search_imdb
from reports import TVReport


def main():
    """
    Scrape the data for It's Always Sunny in Philadelphia
    """
    q = input("Enter a search term for a television show > ")
    results = search_imdb(q)[:10]
    if not results:
        print("No results found! Check the search term.")
        sys.exit(1)

    for num, result in enumerate(results):
        name = result["showname"]
        cat = result["category"]
        date = result["year"]
        print(f"{num+1}. {name}\t({date})\t[{cat}]")
    print()
    while True:
        choice = input("Choose one of the above shows > ")
        try:
            choice = int(choice) - 1
        except ValueError:
            print("Please enter a valid (numerical) choice.\n")
            continue
        try:
            chosen = results[choice]
        except IndexError:
            print("Please enter a number present in the list above.")
            continue
        break

    print(f"You have chosen {chosen['showname']} with ID: {chosen['id']}\n")
    print("Retrieving data...")
    scraper = IMDBScraper(chosen["id"])
    reporter = TVReport(data_provider=scraper)
    print("Generating report...")
    reporter.heatmap()
    reporter.save_file(filename="test", output_dir="./data")
    print("Report saved.")


if __name__ == "__main__":
    main()
