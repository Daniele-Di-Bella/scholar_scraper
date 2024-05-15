import click
from scholar_scraper.scraper import scholar
from scholar_scraper.scraper import search
from scholar_scraper.scraper import arxiv


@click.group()
def cli():
    pass


cli.add_command(scholar)
cli.add_command(search)
cli.add_command(arxiv)

if __name__ == "__main__":
    cli()
