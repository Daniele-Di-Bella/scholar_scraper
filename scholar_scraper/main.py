import click
from scholar_scraper.scraper import scrape
from scholar_scraper.scraper import search


@click.group()
def cli():
    pass


cli.add_command(scrape)
cli.add_command(search)

if __name__ == "__main__":
    cli()
