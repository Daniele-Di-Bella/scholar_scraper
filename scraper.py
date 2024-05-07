import csv
import webbrowser
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate


class scraped:
    def __init__(self, title, link):
        self.title = title
        self.link = link

    def format_title(self):
        var = self.title.replace("…\xa0and", "...")
        var = var.replace("\xa0…", "...")
        var = var.rstrip()
        var = var.lstrip()
        return var

    @staticmethod
    def rating(f_title, keywords: list):
        keywords_l = [element.lower() for element in keywords]
        f_title = f_title.lower()
        N = sum(f_title.count(element) for element in keywords_l)
        score = (N * 100) / len(keywords)
        return score


def scholar_scraper(keywords: list, num_pages, most_recent="yes"):
    papers = []
    page = 0
    current_dateTime = datetime.now()
    current_year = current_dateTime.year
    query = ""
    for i in keywords:
        query = query + "+" + i

    while page < num_pages:
        if most_recent == "yes":
            url = f"https://scholar.google.com/scholar?start={page * 10}&q={query}&hl=en&as_sdt=0,5&as_ylo={current_year}"
        else:
            url = f"https://scholar.google.com/scholar?start={page * 10}&q={query}&hl=en&as_sdt=0,5"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        results = soup.find_all("div", class_="gs_ri")

        for result in results:
            title = result.find("h3", class_="gs_rt").text
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

            paper = scraped(title, link)
            score = scraped.rating(paper.format_title(), keywords)

            papers.append({"Score": score, "Title": paper.format_title(), "Link": paper.link})

        page += 1

    field_names = ["Score", "Title", "Link"]
    with open("papers.csv", "w", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(papers)

    df = pd.read_csv("papers.csv")
    df = df.sort_values(by=["Score"], ascending=False)
    # print(df)

    headers = df.columns.tolist()
    headers.insert(0, 'Index')
    tabula = tabulate(df[["Score", "Title"]], headers=headers, showindex=True, colalign=("left", "left", "left"),
                      tablefmt="simple", maxcolwidths=[5, 5, 120])

    print(tabula)


def opener(csv_file: str):
    print("Are you interested in some of these papers? y/n")
    ans = input()

    if ans == "y":
        print("Write below their indices separated by a comma:")
        indices = input()
        print("Do you want to add more? y/n")
        ans2 = input()

        new_indices = ""
        if ans2 == "y":
            new_indices = input()

        tot_indices = indices + new_indices
        tot_indices = tot_indices.split(',')
        nums = [int(ele.strip()) for ele in tot_indices]
        df = pd.read_csv(csv_file)

        for i in nums:
            webbrowser.open(df.iloc[i]['Link'])

        print("The papers you indicated were opened in the browser")

    else:
        print("Ok")


if __name__ == "__main__":
    scholar_scraper(["sicurezza", "lavoro"], 1)
    opener("papers.csv")
