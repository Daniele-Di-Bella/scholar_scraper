import click
from scholar_scraper import scraper


@click.group()
def cli():
    pass


cli.add_command(scraper.scrape)
cli.add_command(scraper.search)
