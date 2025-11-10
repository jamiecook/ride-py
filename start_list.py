#!/usr/bin/env python

from io import StringIO
import math
import sys
import bs4 as bs
import urllib.request
from matplotlib import pyplot as plt
from numpy import isin
import pandas as pd
import seaborn as sns

splats = [
    "buggy",
    "wissler",
    "cook, jamie",
    "gossow",
    "junjie",
    "abad",
    "schoemaker",
    "weis, gary",
    "leech",
    "angus, brendon",
    "parslow",
]
not_splats = ["wolters"]
hamilton_abbr = ["hamilton", "hwcc"]
lifecycle_abbr = ["lifecycle"]
uq_abbr = ["university", "uq"]
bne_abbr = ["bne", "brisbane"]
sccc_abbr = ["sunshine", "sccc", "sunny"]
mbcc_abbr = ["moreton"]


def plot_race(race_ids, categories=None):
    if not isinstance(race_ids, list):
        race_ids = [race_ids]

    data = [get_riders(f"https://entryboss.cc/races/{race_id}/startlist") for race_id in race_ids]
    df = pd.concat(e[0] for e in data)
    df["strava"] = df.rider.apply(
        lambda x: f"https://www.strava.com/athletes/search?text={x.split(',')[1].strip()}%20{x.split(',')[0]}"
    )
    race_name = data[0][1]

    if categories is None:
        categories = df[df.team == "Hope"].Category.unique()
    print(categories)
    if not set(categories):
        categories = df.Category.unique()

    plot_category(df, categories, race_name)
    return df[df.Category.isin(categories)]


def guess_team(row):
    row.club = "" if isinstance(row.club, float) else row.club
    if "splat" in row.club.lower() or "hope" in row.club.lower() or any([x in row.rider.lower() for x in splats]):
        if not any([x in row.rider.lower() for x in not_splats]):
            return "Hope"
    if "watt bomb" in row.club.lower():
        return "WattBomb"
    if "wolf" in row.club.lower():
        return "WolfTeam"
    if "futuro" in row.club.lower():
        return "Futuro"
    if "argenic" in row.club.lower():
        return "Argenic"
    if "taylor" in row.club.lower():
        return "Taylor Cycles"
    if "rats" in row.club.lower():
        return "RATS"
    if "initiative" in row.club.lower():
        return "WCDI"

    if "solaris" in row.club.lower():
        return "Solaris Racing"
    if "clevr" in row.club.lower():
        return "Clevr Racing"
    if "ipswich" in row.club.lower():
        return "Ipswich CC"
    if "logan" in row.club.lower():
        return "Logan CC"
    if "gold coast" in row.club.lower():
        return "Gold Coast CC"

    if any([x in row.club.lower() for x in mbcc_abbr]):
        return "MBCC"
    if any([x in row.club.lower() for x in bne_abbr]):
        return "BNECC"
    if any([x in row.club.lower() for x in hamilton_abbr]):
        return "Hamilton"
    if any([x in row.club.lower() for x in lifecycle_abbr]):
        return "Lifecycle"
    if any([x in row.club.lower() for x in uq_abbr]):
        return "UQCC"
    if any([x in row.club.lower() for x in sccc_abbr]):
        return "SunnyCoast"
    if any([x in row.club.lower() for x in ["balmoral"]]):
        return "Balmoral"
    if any([x in row.club.lower() for x in ["kangaroo", "kpcc"]]):
        return "KPCC"
    if any([x in row.club.lower() for x in ["redland"]]):
        return "Redlands CC"
    if any([x in row.club.lower() for x in ["darling"]]):
        return "Darling Downs CC"
    return row.club  # "TheRest"


def clean_category(row):
    cat = row.Category

    cat = cat.replace(" (White)", "")

    cat = cat.replace(" (Blue)", "")
    cat = cat.replace(" (Blue/Pink)", "")
    cat = cat.replace(" (Orange)", "")
    cat = cat.replace(" (Orange/Pink)", "")
    cat = cat.replace(" (Yellow)", "")
    cat = cat.replace(" (Yellow/Pink)", "")
    cat = cat.replace(" (Green)", "")
    cat = cat.replace(" (Green/Pink)", "")
    return cat


# url = "https://entryboss.cc/races/18894/startlist"
def get_riders(url):
    source = urllib.request.urlopen(url).read()
    soup = bs.BeautifulSoup(source, "lxml")

    table = soup.find_all("table")
    df = pd.read_html(StringIO(str(table)))[0]
    df.rename(columns={"Club/Team": "club", "Participant": "rider"}, inplace=True)
    df["team"] = df.apply(guess_team, axis=1)
    df["Category"] = df.apply(clean_category, axis=1)

    # search on page for div class block songbook and extract songtext between <p>
    headings = soup.find_all("div", attrs={"class": "panel-heading"})
    for item in headings:
        race_name = item.text

    return df, race_name


# acq - aus-cycling-qld
def get_races(org="acq"):
    url = f"https://entryboss.cc/calendar/{org}"
    source = urllib.request.urlopen(url).read()
    # soup = bs.BeautifulSoup(source,'lxml')
    soup = bs.BeautifulSoup(source, "html.parser")

    links = [
        f"https://entryboss.cc{list(e.children)[0]['href']}/startlist"
        for e in soup.findAll("div", attrs={"class": "fixture-name"})
    ]

    dates = [e.text.strip() for e in soup.findAll("div", attrs={"class": "fixture-date"})]
    names = [e.text.strip() for e in soup.findAll("div", attrs={"class": "fixture-name"})]
    courses = [e.text.strip() for e in soup.findAll("div", attrs={"class": "fixture-course"})]
    return pd.DataFrame({"date": dates, "name": names, "link": links}).assign(club=org)

    return divList
    print(divList)

    table = soup.find_all("table")
    df = pd.read_html(StringIO(str(table)))[0]
    # df.rename(columns={'Club/Team': 'club', 'Participant': 'rider'}, inplace=True)
    return df


def plot_category(df, categories, race_name):
    num_rows = math.ceil(len(categories) / 2)
    fig, axes = plt.subplots(num_rows, 2, figsize=(20, 6 * num_rows))
    if num_rows > 1:
        axes = [a for a_ in axes for a in a_]
    for count, c in enumerate(categories):
        c = [c] if isinstance(c, str) else c
        df_ = df[df.Category.isin(c)]
        if df_.empty:
            print(f"no riders in Category: {c}, available categories are {df.Category.unique()}")
        # display(df_)
        num_riders = df_.shape[0]
        df_ = df_.groupby(["team"]).agg({"club": len})
        # df_ = df_.groupby(['Category', 'team'], group_keys=False)
        df_ = df_.apply(lambda x: x.sort_values(ascending=False))

        splatt_red = (0.7686274509803922, 0.3058823529411765, 0.3215686274509804)
        hope_orange = (243.0 / 255, 158.0 / 255, 29.0 / 255)
        palette = {c: (0.7, 0.7, 0.7) if c != "Hope" else hope_orange for c in df["team"].unique()}

        sns.set(font_scale=1)
        ax = sns.barplot(df_, x="team", y="club", hue="team", palette=palette, ax=axes[count], errorbar=None)
        ax.tick_params(axis="x", rotation=45)
        ax.set_title(f"Category {c} - {num_riders} riders")
        ax.set_xlabel("")
    fig.suptitle(race_name)


if __name__ == "__main__":
    df = get_riders(sys.argv[0])
    plot_category(df, "B")
    plot_category(df, "C")
    plot_category(df, "D")
