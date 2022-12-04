import json
import pprint
import re
from bs4 import BeautifulSoup
import requests


url = "https://pokemondb.net/pokedex/all"

gen_type_removal = {
    "gen_1": {"steel", "fairy"},
    "gen_2": {"fairy"},
    "gen_3": {"fairy"},
    "gen_4": {"fairy"},
    "gen_5": {"fairy"},
    "gen_6": {"fairy"},
    "gen_7": {}
}


#response = requests.get(url)

#soup = BeautifulSoup(response.text, "html.parser")

with open("type_html.txt", "r") as f:
    data = f.read()

soup = BeautifulSoup(data, "html.parser")


table = soup.find("table", {"id": "pokedex"})
tbody = table.find("tbody")

master = {gen: {} for gen in gen_type_removal.keys()}
for tr in tbody.find_all("tr"):

    num = int(tr.find("td", {"class": "cell-num cell-fixed"}).text)
    name_cell = tr.find("td", {"class": "cell-name"})
    type_cell = tr.find("td", {"class": "cell-icon"})

    if name_cell.find("small"):
        continue

    name = name_cell.text
    pokemon = re.sub("[^a-zA-Z0-9_-]", "", name.lower())
    types = [e.text.lower() for e in type_cell.find_all("a")]
    print(num, name, types)

    for gen in master.keys():
        master[gen].setdefault(pokemon, {})
        master[gen][pokemon] = {
            "key": pokemon,
            "number": num,
            "types": [t for t in types if t not in gen_type_removal[gen]],
            "display_name": name
        }

pprint.pprint(master)
for key, d in master.items():
    with open("../resources/pokemon_data/%s.json" % key, "w") as f:
        json.dump(d, f)

