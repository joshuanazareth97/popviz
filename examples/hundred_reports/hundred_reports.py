from pathlib import Path

from regex import regex as re

from scraper import IMDBScraper
from scraper.utils import get_parsed_webpage
from reports.tv_report_gen import TVReport


def get_show_ids():
    webpage = get_parsed_webpage("https://www.imdb.com/chart/toptv/")
    list_div = webpage.find("div", class_="lister")
    lst = list_div.select_one("table.chart tbody ")
    for num, row in enumerate(lst.children):
        try:
            title_cell = row.find("td", class_="titleColumn")
            link = title_cell.find("a")
            title = link.text.strip()
            id_ = get_id_from_link(link["href"])
            yield title, id_
        except:
            continue


def get_id_from_link(link):
    result = re.search("\/title\/([A-Za-z0-9]+)\/", link)
    if result:
        return result.group(1)
    return ""

if __name__ == "__main__":
    main()