import csv
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate


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
            title = title.replace("…\xa0and", "...")
            title = title.replace("\xa0…", "...")
            title = title.rstrip()
            title = title.lstrip()
            title_l = title.lower()
            keywords_l = [element.lower() for element in keywords]
            N = sum(title_l.count(element) for element in keywords_l)
            rating = (N * 5) / len(keywords)
            link = result.find("a")["href"]
            papers.append({"Rating": rating, "Title": title, "Link": link})

        page += 1

    field_names = ["Rating", "Title", "Link"]
    with open("csvs/papers.csv", "w", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(papers)

    df = pd.read_csv("csvs/papers.csv")
    df = df.sort_values(by=["Rating"], ascending=False)
    # print(df)

    headers = df.columns.tolist()
    headers.insert(0, 'Index')
    tabula = tabulate(df[["Rating", "Title"]], headers=headers, showindex=True, colalign=("left", "left", "left"),
                      tablefmt="simple", maxcolwidths=[5, 5, 120])

    print(tabula)


if __name__ == "__main__":
    scholar_scraper(["planktonic", "communities"], 5)
