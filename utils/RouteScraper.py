
import requests
from bs4 import BeautifulSoup



with open("route_parser_test.txt", "r", encoding="utf8") as f:
    data = f.read()

soup = BeautifulSoup(data, "html.parser")

pokemon_header = soup.find(id="Pokémon").parent

gen_header = pokemon_header.find_next_sibling("h4")

gen_id = gen_header.find("span")["id"]

table = gen_header.find_next_sibling("table")
print(table)
print()
print(gen_header.attrs)


print()

