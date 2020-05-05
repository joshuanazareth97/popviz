from regex import regex as re
import urllib.parse

from scraper.utils import get_parsed_webpage


def get_data_from_row(row):
    try:
        text = row.text
    except AttributeError:
        return
    match = re.search(r"(.+) (\(.+\)) (\(.+\))", text)
    try:
        name = match.group(1).strip()
        year = match.group(2).strip("()")
        cat = match.group(3).strip("()")
    except AttributeError:
        return
    if "series" not in cat.lower():
        return
    # print(name, year, cat)
    try:
        link = row.select_one(".result_text a").get("href").strip()
        link_match = re.search(r"title\/(tt\d+)", link)
        show_id = link_match.group(1)
    except AttributeError:
        return
    return dict(showname=name, category=cat, year=year, id=show_id)


def search(query):
    encoded = urllib.parse.quote(query)
    url = f"https://www.imdb.com/find?q={encoded}&s=tt&ttype=tv"
    webpage = get_parsed_webpage(url)
    lst = webpage.find("table", class_="findList")
    return list(
        filter(
            lambda show: show is not None,
            (get_data_from_row(child) for child in lst.children),
        )
    )
