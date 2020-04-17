from tqdm import tqdm

from scraper import IMDBScraper
from reports import TVReport

def main():
    show_data = []
    iasip = IMDBScraper("tt0944947")
    for season in tqdm(iasip.get_all_seasons(), desc="Retrieving data season-wise", total=iasip.latest_season):
        show_data.append(season)
    reporter = TVReport(data=show_data)
    

if __name__ == "__main__":
    main()