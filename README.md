# PopViz

A command-line tool written in Python to scrape ratings data of TV Series from IMDb and display the results in a beautiful chart.

## To Do

* Implement a logging system for the scraper

* Add a frontend to access this tool in a browser

* Add templates support to the reporter

* Add multiple types of graphs to reporter (currently supports heatmaps)

## Getting Started

This app can be run in several ways, depending on your use case.

### Installing

1. Clone this repository, and change into the directory.

    ``` git clone https://github.com/joshuanazareth97/popviz.git && cd popviz ```

2. Install the app for regular use:

    ``` pip install . ```

3. Install the app for development use, along with all development dependencies:

    ``` pip install -r requirements.txt ```

### Example Usage

After installation, run the app using:

* as a command-line utility: 
    ```
    > popviz [-h] [-s SEARCH | -i ID] [-o OUTPUT]
    ```

    ```
    -h, --help                    show this help message and exit
    -s SEARCH, --search SEARCH    Search for a television show.
    -i ID, --id ID                Directly provide the IMDb ID of a television show.
    -o OUTPUT, --output OUTPUT    Specify a filename for the output. Defaults to the name of the show.
    
    ```

* or in your project by importing the package: 
    ``` 
        # Scrape the data for It's Aways Sunny in Phladelphia

        from scraper import IMDBScraper
        from tqdm import tqdm

        iasip = IMDBScraper("tt0472954")
        desc = "Retrieving data season-wise"
        for season in iasip.seasons:
            print(f"Season {season['number']}")
            print(
                map(lambda e: f"Episode {e['episode_number']}: {e['title']}",
                    season["episodes"]),
                end="\n\n"
            )

    ```
See the [examples](/examples) directory for more.


## Built With

* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - Used to parse the TV Series Data from IMDb
* [Seaborn](https://seaborn.pydata.org/) - Used to generate the figures.
* [Setuptools](https://setuptools.readthedocs.io/en/latest/) - Dependency Management

Among many others.

## Versioning

For the versions available, see the [tags on this repository](https://github.com/joshuanazareth97/popviz/tags). 

## Author(s)

**Joshua Nazareth** - [Website](https://joshuanazareth97.github.io)

See also the list of [contributors](https://github.com/joshuanazareth97/popviz/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

The original idea for this can be attributed to the [r/dataisbeautiful](https://www.reddit.com/r/dataisbeautiful) subreddit, where reports of this nature had become a trend, for a while.