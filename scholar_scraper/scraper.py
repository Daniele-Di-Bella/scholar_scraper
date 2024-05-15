import csv
import os
import webbrowser
from datetime import datetime
import click
import arxivscraper
import pandas as pd
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from tabulate import tabulate


class scraped:
    def __init__(self, author, title, link):
        self.author = author
        self.title = title
        self.link = link

    def format_title(self):
        var = self.title.replace("…\xa0and", "...")
        var = var.replace("\xa0…", "...")
        var = var.rstrip()
        var = var.lstrip()
        return var

    def format_author(self):
        x = self.author.split(",")
        return x[0]

    @staticmethod
    def rating(f_title, keywords: list):
        keywords_l = [element.lower() for element in keywords]
        f_title = f_title.lower()
        N = sum(f_title.count(element) for element in keywords_l)
        score = (N * 100) / len(keywords)
        return score


@click.command("scholar", help="Launch the scraping activity on Google Scholar")
@click.argument("keywords", nargs=-1)
@click.option("-n", "--num_pages", type=click.INT, default=1, help="The number of Google Scholar "
                                                                   "pages that you want to scrape")
@click.option("-m", "--most_recent", is_flag=True, help="If set on True, this option filter the "
                                                        "papers starting from the current year")
def scholar(keywords, num_pages, most_recent):
    """
    This command launch the scraping activity on the basis of a set of keywords specified by the user.
    The order in which the keywords are written matters.
    """
    papers = []
    page = 0
    current_dateTime = datetime.now()
    current_year = current_dateTime.year
    query = ""
    for i in keywords:
        query = query + "+" + i

    pbar = tqdm(total=num_pages)  # Graphical progression bar, to report to the user how much time is left
    # before the end of the scraping operation

    while page < num_pages:
        if most_recent:
            url = f"https://scholar.google.com/scholar?start={page * 10}&q={query}&hl=en&as_sdt=0,5&as_ylo={current_year}"
        else:
            url = f"https://scholar.google.com/scholar?start={page * 10}&q={query}&hl=en&as_sdt=0,5"

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print()  # Just to detach the error signal from the tqdm progress bar
            print("An error occurred during a request to Google Scholar, the", e)
            return

        soup = BeautifulSoup(response.content, "html.parser")
        results = soup.find_all("div", class_="gs_ri")

        for result in results:
            title = result.find("h3", class_="gs_rt").text
            # The two following blocks exclude books from the results that scrape() will provide.
            if result.find("span", class_="gs_ct1") is not None:
                doc_type1 = result.find("span", class_="gs_ct1").text
                if doc_type1 == "[BOOK]":
                    continue
                else:
                    title = title.replace(doc_type1, '')
            if result.find("span", class_="gs_ct2") is not None:
                doc_type2 = result.find("span", class_="gs_ct2").text
                if doc_type2 == "[B]":
                    continue
                else:
                    title = title.replace(doc_type2, "")

            link = result.find("a")["href"]
            author = result.find("div", class_="gs_a").text

            paper = scraped(author, title, link)
            score = scraped.rating(paper.format_title(), keywords)

            papers.append({"Score": score, "Author": paper.format_author(), "Title": paper.format_title(),
                           "Link": paper.link})

        page += 1
        pbar.update(1)
    pbar.close()

    print("The request(s) to Google Scholar was/were successful")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    field_names = ["Score", "Author", "Title", "Link"]

    with open(os.path.join(current_dir, "papers.txt"), "w", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(papers)

    df = pd.read_csv(os.path.join(current_dir, "papers.txt"))
    df = df.sort_values(by=["Score"], ascending=False)
    # print(df)

    headers = df.columns.tolist()
    headers.insert(0, "Index")
    tabula = tabulate(df[["Score", "Author", "Title"]], headers=headers, showindex=True,
                      colalign=("left", "left", "left", "left"),
                      tablefmt="simple", maxcolwidths=[5, 5, 10, 90])

    print(tabula)


@click.command("search", help="Open the chosen articles in the browser")
@click.argument("indices", type=click.INT, nargs=-1)
def search(indices):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(current_dir, "papers.txt"))
    for i in indices:
        webbrowser.open(df.iloc[i]['Link'])
    print("The papers you indicated were opened in the browser")


@click.command("arxiv", help="Launch the scraping activity on arXiv")
@click.argument("category")
@click.argument("keywords", nargs=-1)
def arxiv(category, keywords):
    current_dateTime = datetime.now()
    year = current_dateTime.year
    month = current_dateTime.month
    day = current_dateTime.day
    str_dateTime = f"{year}-{month}-{day}"

    scraper = arxivscraper.Scraper(category=category, date_until=str_dateTime,
                                   filters={'title': keywords})
    output = scraper.scrape()
    print(output)

    cols = ["id", "title", "categories", "abstract", "doi", "created", "updated", "authors"]
    df = pd.DataFrame(output, columns=cols)
    df.drop(["id", "abstract", "created", "updated"])

    scores = []
    for index, row in df.iterrows():
        obj = scraped(row["authors"], row["title"], row["doi"])
        scores.append(scraped.rating(obj.title, keywords))

    df.insert(1, "Score", scores)

    headers = ["Index", "Score", "Title", "Authors"]
    tabula = tabulate(df[["Score", "title", "authors"]], headers=headers, showindex=True,
                      colalign=("left", "left", "left", "left"),
                      tablefmt="simple", maxcolwidths=[5, 5, 10, 90])

    print(tabula)
