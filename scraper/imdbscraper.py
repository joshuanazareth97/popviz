from scraper.utils import get_parsed_webpage


class IMDBScraper:
    """
        Utility class which allows the retrieval of episode related data from IMDb.
        Instantiated with series ID(s)
    """

    BASE_URL = "https://www.imdb.com/title"

    def __init__(self, series_ID):
        self.series = series_ID
        self.url = f"{self.BASE_URL}/{self.series}"
        self.latest_season = self._get_latest_season()

    def _get_latest_season(self):
        webpage = get_parsed_webpage(f"{self.url}/episodes?season=0")
        latest_season = (
            webpage.find("h3", id="episode_top")
            .text.strip()
            .replace("Season\xa0", "")
        )
        return int(latest_season)

    def get_show_data(self):
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
        return data

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
        image_div = episode_tag.select("div.image img")[0]
        image_url = image_div["src"]
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
        except AttributeError:
            rating = ""
            num_ratings = ""

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
        for season in range(1, self.latest_season + 1):
            yield self.get_season_data(season=season)


    def get_season_data(self, season=1):
        """
            Returns a dictionary with key "episodes",
            for the season no. specified in the parameter `season`
        """
        season = int(season)
        episode_list_url = f"{self.url}/episodes?season={season}"
        webpage = get_parsed_webpage(episode_list_url)
        data = {
            "number": season,
            "episodes": []
        }
        list_wrapper = webpage.select("div.list #episodes_content")[0]
        epsiode_list = list_wrapper.find("div", class_="eplist")
        for episode in epsiode_list.find_all("div", class_="list_item"):
            data["episodes"].append(IMDBScraper._get_episode_data(episode))
        return data


if __name__ == "__main__":
    pass
