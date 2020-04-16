from scraper import IMDBScraper
from tqdm import tqdm

def main():
    """
    Scrape the data for It's Always Sunny in Philadelphia
    """
    iasip = IMDBScraper("tt0472954")
    for season in tqdm(iasip.get_all_seasons(), desc="Retrieving data season-wise", total=iasip.latest_season):
        tqdm.write(f"Season {season['number']}")
        tqdm.write(
            "\n".join(map(lambda e: f"Episode {e['episode_number']}: {e['title']}",
                 season["episodes"])),
            end="\n\n"
        )

if __name__ == "__main__":
    main()
