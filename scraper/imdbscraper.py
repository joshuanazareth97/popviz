from scraper.utils import get_parsed_webpage
from pathlib import Path
import json

from tqdm import tqdm


class IMDBScraper:
    """
        Scraper class which allows the retrieval of episode related data from IMDb.
        Instantiated with series ID
    """

    __privates__ = ["cached_episode_data", "episode_data"]

    BASE_URL = "https://www.imdb.com/title"

    def __init__(self, series_ID, log=True):
        self.log = True
        self.series = series_ID
        self.url = f"{self.BASE_URL}/{self.series}"
        self.data_file = Path.cwd() / f"data/{self.series}.json"
        self.cached_episode_data = []
        self.episode_data = []
        if self.data_file.exists():
            with self.data_file.open() as fp:
                self.cached_episode_data = json.load(fp)
        self._get_show_data()
        self._get_latest_season()

    @property
    def seasons(self):
        if self.latest_season["number"] <= 1:
            return [self.latest_season]
        if self.cached_episode_data:
            return self.cached_episode_data
        elif not self.episode_data:
            self.get_all_seasons()
        return self.episode_data

    @property
    def show_metadata(self):
        if self.show_data:
            return self.show_data
        else:
            raise ValueError("No show data found. Are you sure you have instantiated the object properly?")

    def _get_latest_season(self):
        webpage = get_parsed_webpage(f"{self.url}/episodes?season=0")
        self.latest_season = self._get_season_data(webpage)
        # Check to see if the latest season(s) are empty empty - Edge case
        while all([episode["rating"] == '' for episode in self.latest_season["episodes"]]):
            latest = self.latest_season["number"] - 1
            webpage = get_parsed_webpage(f"{self.url}/episodes?season={latest}")
            self.latest_season = self._get_season_data(webpage)


    def _get_show_data(self):
        """
            Returns a dictionary of show level data
        """
        webpage = get_parsed_webpage(self.url)
        details = webpage.find(class_="title_bar_wrapper")
        title = details.select(".title_wrapper h1")[0].text.strip()
        rating = details.select(".ratings_wrapper .ratingValue span")[0].text.strip()
        num_ratings = details.select(".ratings_wrapper a span.small")[0].text.strip()
        num_episodes = (
            webpage.find(class_="navigation_panel")
            .find(class_="bp_sub_heading")
            .text.replace("episodes", "")
            .strip()
        )
        additional_details_tag = details.find(class_="subtext")
        additional_details = IMDBScraper._get_additional_details(additional_details_tag)

        plot_details = webpage.find(class_="plot_summary")
        summary = plot_details.find(class_="summary_text").text.strip()
        cast = plot_details.find_all(class_="credit_summary_item")
        if len(cast) == 1:
            stars = cast[0]
            creators = []
        else:
            creators, stars = cast
            creators = list(map(lambda x: x.text.strip(), creators("a")))
        stars = list(map(lambda x: x.text.strip(), stars("a")))

        poster_div = webpage.find("div", class_="poster")
        poster = poster_div.find("img")["src"]
        data = dict(
            title=title,
            rating=rating,
            num_ratings=num_ratings,
            num_episodes=num_episodes,
            plot_summary=summary,
            creators=creators,
            stars=stars,
            poster_url=poster,
        )
        data.update(additional_details)
        self.show_data = data


    @staticmethod
    def _get_additional_details(details):
        remove_whitespace = lambda x: x.strip()
        additional_data = list(map(remove_whitespace, details.text.split("|")))
        maturity = ""
        if len(additional_data) == 4:
            maturity = additional_data[0]
            additional_data = additional_data[1:]
        try:
            ep_time, tags, date = additional_data
        except:
            return {}
        tags = list(map(remove_whitespace, tags.split(",")))
        return {
            "tags": tags,
            "time_per_episode": ep_time,
            "running_date": date,
            "maturity": maturity,
        }

    @staticmethod
    def _get_episode_data(episode_tag):
        info_div = episode_tag.find("div", class_="info")
        try:
            ep_number = info_div.find("meta")["content"].strip()
        except AttributeError:
            ep_number = ""
        try:
            airdate = info_div.find("div", class_="airdate").text.strip()
        except AttributeError:
            airdate = ""
        try:
            plot_summary = info_div.find("div", class_="item_description").text.strip()
        except AttributeError:
            airdate = ""
        rating_div = info_div.find("div", "ipl-rating-star")
        try:
            rating = rating_div.select("span.ipl-rating-star__rating")[0].text.strip()
            num_ratings = rating_div.select("span.ipl-rating-star__rating")[0].text.strip()
        except (IndexError, AttributeError):
            rating = ""
            num_ratings = ""

        try:
            image_div = episode_tag.select("div.image img")[0]
            image_url = image_div["src"]
        except (IndexError, AttributeError):
            image_url = ""

        try:
            title = info_div.select_one("strong a").text.strip()
        except AttributeError:
            title = ""

        return dict(
            title=title,
            airdate=airdate,
            episode_number=ep_number,
            rating=rating,
            num_ratings=num_ratings,
            plot=plot_summary,
            poster_url=image_url
        )

    def get_all_seasons(self):
        """
            Returns a generator of dictionaries (seasons),
            each contains an "episodes" key with a list of episodes for that season.
        """
        seasons = range(1, self.latest_season["number"])
        if self.log:
            seasons = tqdm(seasons, desc="Retrieving data season-wise")
        for season in seasons:
            episode_list_url = f"{self.url}/episodes?season={season}"
            webpage = get_parsed_webpage(episode_list_url)
            self.episode_data.append(self._get_season_data(season_page=webpage))
        self.episode_data.append(self.latest_season)

    def _get_season_data(self, season_page):
        """
            Returns a dictionary with key "episodes",
            by parsing the html page provided in the webpage param.
        """
        season = (
            season_page.find("h3", id="episode_top")
            .text.strip()
            .replace("Season\xa0", "")
        )
        data = {
            "number": int(season),
            "episodes": []
        }
        list_wrapper = season_page.select("div.list #episodes_content")[0]
        epsiode_list = list_wrapper.find("div", class_="eplist")
        for episode in epsiode_list.find_all("div", class_="list_item"):
            data["episodes"].append(IMDBScraper._get_episode_data(episode))
        return data

    def dump(self, filename=None, data_dir="./data"):
        if not self.episode_data:
            if self.log: print("No new data loaded, so there is nothing to dump.")
            return
        if filename is not None:
            self.data_file = Path(data_dir) / filename
        if self.data_file.exists():
            if self.log: print("Overwriting data file...")
        with self.data_file.open("w+") as fp:
            json.dump(self.episode_data, fp)
        if self.log: print("File written successfully.")
        

if __name__ == "__main__":
    print("Please run this scraper by importing the IMDBScraper class <scraper.IMDBScraper>")
