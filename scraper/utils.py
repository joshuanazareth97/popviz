import requests
from bs4 import BeautifulSoup as bs

def get_parsed_webpage(url, parser="lxml"):
    """
    Takes a url string as paramter, makes a GET request,
    and then instantiates a BeautifulSoup object with the parser specified.
    Default parser is lxml.
    """
    resp = requests.get(url)
    soup = bs(resp.text, parser)
    return soup
    