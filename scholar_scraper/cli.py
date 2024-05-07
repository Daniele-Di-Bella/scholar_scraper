# Entry for Command Line Interface
import click
import scraper


@click.group()
def cli():
    pass


cli.add_command(scraper.scrape)
cli.add_command(scraper.search)


