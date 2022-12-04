import json
import os.path

import requests
from bs4 import BeautifulSoup
import pprint
import re
import urllib.parse

from PokemonGameDataAdapter import PokemonGameDataAdapter


class SerebiiPokearthAdapter(PokemonGameDataAdapter):
    def __init__(self, *args, **kwargs):
        super(SerebiiPokearthAdapter, self).__init__(*args, **kwargs)

        self.pre_url = "https://www.serebii.net/"

        self.gen_route_changes_map = {
            "gen_1": {
                "pokemontower": "lavendertown",
                "safarizone": "fuschiacity",
                "pokemonmansion": "cinnabarisland"
            },
            "gen_2": {
                "pokemontower": "lavendertown",
                "safarizone": "fuschiacity",
                "pokemonmansion": "cinnabarisland",
                "burnedtower": "ecruteakcity",
                "tintower": "ecruteakcity",
                "belltower": "ecruteakcity",
                "silvercave": "mtsilver"
            },
            "gen_3": {

            }
        }
        self.gen_url_map = {
            "gen_1": ["/pokearth/kanto/1st/route1.shtml",
                      "/pokearth/kanto/1st/route2.shtml",
                      "/pokearth/kanto/1st/route3.shtml",
                      "/pokearth/kanto/1st/route4.shtml",
                      "/pokearth/kanto/1st/route5.shtml",
                      "/pokearth/kanto/1st/route6.shtml",
                      "/pokearth/kanto/1st/route7.shtml",
                      "/pokearth/kanto/1st/route8.shtml",
                      "/pokearth/kanto/1st/route9.shtml",
                      "/pokearth/kanto/1st/route10.shtml",
                      "/pokearth/kanto/1st/route11.shtml",
                      "/pokearth/kanto/1st/route12.shtml",
                      "/pokearth/kanto/1st/route13.shtml",
                      "/pokearth/kanto/1st/route14.shtml",
                      "/pokearth/kanto/1st/route15.shtml",
                      "/pokearth/kanto/1st/route16.shtml",
                      "/pokearth/kanto/1st/route17.shtml",
                      "/pokearth/kanto/1st/route18.shtml",
                      "/pokearth/kanto/1st/route19.shtml",
                      "/pokearth/kanto/1st/route20.shtml",
                      "/pokearth/kanto/1st/route21.shtml",
                      "/pokearth/kanto/1st/route22.shtml",
                      "/pokearth/kanto/1st/route23.shtml",
                      "/pokearth/kanto/1st/route24.shtml",
                      "/pokearth/kanto/1st/route25.shtml",
                      "/pokearth/kanto/1st/ceruleancave.shtml",
                      "/pokearth/kanto/1st/ceruleancity.shtml",
                      "/pokearth/kanto/1st/cinnabarisland.shtml",
                      "/pokearth/kanto/1st/celadoncity.shtml",
                      "/pokearth/kanto/1st/diglett'scave.shtml",
                      "/pokearth/kanto/1st/fuchsiacity.shtml",
                      "/pokearth/kanto/1st/indigoplateau.shtml",
                      "/pokearth/kanto/1st/lavendertown.shtml",
                      "/pokearth/kanto/1st/mt.moon.shtml",
                      "/pokearth/kanto/1st/pallettown.shtml",
                      "/pokearth/kanto/1st/pewtercity.shtml",
                      "/pokearth/kanto/1st/pokemonmansion.shtml",
                      "/pokearth/kanto/1st/pokemontower.shtml",
                      "/pokearth/kanto/1st/powerplant.shtml",
                      "/pokearth/kanto/1st/rocktunnel.shtml",
                      "/pokearth/kanto/1st/rockethideout.shtml",
                      "/pokearth/kanto/1st/safarizone.shtml",
                      "/pokearth/kanto/1st/saffroncity.shtml",
                      "/pokearth/kanto/1st/seafoamislands.shtml",
                      "/pokearth/kanto/1st/silphco.shtml",
                      "/pokearth/kanto/1st/ssanne.shtml",
                      "/pokearth/kanto/1st/undergroundpath5-6.shtml",
                      "/pokearth/kanto/1st/undergroundpath7-8.shtml",
                      "/pokearth/kanto/1st/vermilioncity.shtml",
                      "/pokearth/kanto/1st/victoryroad.shtml",
                      "/pokearth/kanto/1st/viridiancity.shtml",
                      "/pokearth/kanto/1st/viridianforest.shtml",
                      ],
            "gen_2": ["/pokearth/johto/2nd/route29.shtml",
                      "/pokearth/johto/2nd/route30.shtml",
                      "/pokearth/johto/2nd/route31.shtml",
                      "/pokearth/johto/2nd/route32.shtml",
                      "/pokearth/johto/2nd/route33.shtml",
                      "/pokearth/johto/2nd/route34.shtml",
                      "/pokearth/johto/2nd/route35.shtml",
                      "/pokearth/johto/2nd/route36.shtml",
                      "/pokearth/johto/2nd/route37.shtml",
                      "/pokearth/johto/2nd/route38.shtml",
                      "/pokearth/johto/2nd/route39.shtml",
                      "/pokearth/johto/2nd/route40.shtml",
                      "/pokearth/johto/2nd/route41.shtml",
                      "/pokearth/johto/2nd/route42.shtml",
                      "/pokearth/johto/2nd/route43.shtml",
                      "/pokearth/johto/2nd/route44.shtml",
                      "/pokearth/johto/2nd/route45.shtml",
                      "/pokearth/johto/2nd/route46.shtml",
                      "/pokearth/johto/2nd/route47.shtml",
                      "/pokearth/johto/2nd/route48.shtml",
                      "/pokearth/johto/2nd/azaleatown.shtml",
                      "/pokearth/johto/2nd/battlefrontier.shtml",
                      "/pokearth/johto/2nd/battletower.shtml",
                      "/pokearth/johto/2nd/bellchimetrail.shtml",
                      "/pokearth/johto/2nd/belltower.shtml",
                      "/pokearth/johto/2nd/blackthorncity.shtml",
                      "/pokearth/johto/2nd/burnedtower.shtml",
                      "/pokearth/johto/2nd/cherrygrovecity.shtml",
                      "/pokearth/johto/2nd/cianwoodcity.shtml",
                      "/pokearth/johto/2nd/cliffcave.shtml",
                      "/pokearth/johto/2nd/cliffedgegate.shtml",
                      "/pokearth/johto/2nd/darkcave.shtml",
                      "/pokearth/johto/2nd/dragon'sden.shtml",
                      "/pokearth/johto/2nd/ecruteakcity.shtml",
                      "/pokearth/johto/2nd/embeddedtower.shtml",
                      "/pokearth/johto/2nd/frontieraccess.shtml",
                      "/pokearth/johto/2nd/goldenrodcity.shtml",
                      "/pokearth/johto/2nd/goldenrodunderground.shtml",
                      "/pokearth/johto/2nd/icepath.shtml",
                      "/pokearth/johto/2nd/ilexforest.shtml",
                      "/pokearth/johto/2nd/lakeofrage.shtml",
                      "/pokearth/johto/2nd/mahoganytown.shtml",
                      "/pokearth/johto/2nd/mt.mortar.shtml",
                      "/pokearth/johto/2nd/silvercave.shtml",
                      "/pokearth/johto/2nd/nationalpark.shtml",
                      "/pokearth/johto/2nd/newbarktown.shtml",
                      "/pokearth/johto/2nd/olivinecity.shtml",
                      "/pokearth/johto/2nd/pokeathlondome.shtml",
                      "/pokearth/johto/2nd/radiotower.shtml",
                      "/pokearth/johto/2nd/rockethideout.shtml",
                      "/pokearth/johto/2nd/ruinsofalph.shtml",
                      "/pokearth/johto/2nd/safarizone.shtml",
                      "/pokearth/johto/2nd/safarizonegate.shtml",
                      "/pokearth/johto/2nd/shininglighthouse.shtml",
                      "/pokearth/johto/2nd/sinjohruins.shtml",
                      "/pokearth/johto/2nd/slowpokewell.shtml",
                      "/pokearth/johto/2nd/sprouttower.shtml",
                      "/pokearth/johto/2nd/ssaqua.shtml",
                      "/pokearth/johto/2nd/tintower.shtml",
                      "/pokearth/johto/2nd/unioncave.shtml",
                      "/pokearth/johto/2nd/violetcity.shtml",
                      "/pokearth/johto/2nd/whirlislands.shtml",
                      "/pokearth/kanto/2nd/route1.shtml",
                      "/pokearth/kanto/2nd/route2.shtml",
                      "/pokearth/kanto/2nd/route3.shtml",
                      "/pokearth/kanto/2nd/route4.shtml",
                      "/pokearth/kanto/2nd/route5.shtml",
                      "/pokearth/kanto/2nd/route6.shtml",
                      "/pokearth/kanto/2nd/route7.shtml",
                      "/pokearth/kanto/2nd/route8.shtml",
                      "/pokearth/kanto/2nd/route9.shtml",
                      "/pokearth/kanto/2nd/route10.shtml",
                      "/pokearth/kanto/2nd/route11.shtml",
                      "/pokearth/kanto/2nd/route12.shtml",
                      "/pokearth/kanto/2nd/route13.shtml",
                      "/pokearth/kanto/2nd/route14.shtml",
                      "/pokearth/kanto/2nd/route15.shtml",
                      "/pokearth/kanto/2nd/route16.shtml",
                      "/pokearth/kanto/2nd/route17.shtml",
                      "/pokearth/kanto/2nd/route18.shtml",
                      "/pokearth/kanto/2nd/route19.shtml",
                      "/pokearth/kanto/2nd/route20.shtml",
                      "/pokearth/kanto/2nd/route21.shtml",
                      "/pokearth/kanto/2nd/route22.shtml",
                      "/pokearth/kanto/2nd/route23.shtml",
                      "/pokearth/kanto/2nd/route24.shtml",
                      "/pokearth/kanto/2nd/route25.shtml",
                      "/pokearth/kanto/2nd/route26.shtml",
                      "/pokearth/kanto/2nd/route27.shtml",
                      "/pokearth/kanto/2nd/route28.shtml",

                      "/pokearth/kanto/2nd/ceruleancave.shtml",
                      "/pokearth/kanto/2nd/ceruleancity.shtml",
                      "/pokearth/kanto/2nd/cinnabarisland.shtml",
                      "/pokearth/kanto/2nd/celadoncity.shtml",
                      "/pokearth/kanto/2nd/diglett'scave.shtml",
                      "/pokearth/kanto/2nd/fuchsiacity.shtml",
                      "/pokearth/kanto/2nd/indigoplateau.shtml",
                      "/pokearth/kanto/2nd/lavendertown.shtml",
                      "/pokearth/kanto/2nd/mt.moon.shtml",
                      "/pokearth/kanto/2nd/pallettown.shtml",
                      "/pokearth/kanto/2nd/pewtercity.shtml",
                      "/pokearth/kanto/2nd/pokemonmansion.shtml",
                      "/pokearth/kanto/2nd/pokemontower.shtml",
                      "/pokearth/kanto/2nd/powerplant.shtml",
                      "/pokearth/kanto/2nd/rocktunnel.shtml",
                      "/pokearth/kanto/2nd/rockethideout.shtml",
                      "/pokearth/kanto/2nd/safarizone.shtml",
                      "/pokearth/kanto/2nd/saffroncity.shtml",
                      "/pokearth/kanto/2nd/seafoamislands.shtml",
                      "/pokearth/kanto/2nd/silphco.shtml",
                      "/pokearth/kanto/2nd/ssanne.shtml",
                      "/pokearth/kanto/2nd/undergroundpath5-6.shtml",
                      "/pokearth/kanto/2nd/undergroundpath7-8.shtml",
                      "/pokearth/kanto/2nd/vermilioncity.shtml",
                      "/pokearth/kanto/2nd/victoryroad.shtml",
                      "/pokearth/kanto/2nd/viridiancity.shtml",
                      "/pokearth/kanto/2nd/viridianforest.shtml",
                      "/pokearth/kanto/2nd/tojhofalls.shtml",
                      ],
            "gen_3": ["/pokearth/hoenn/3rd/route101.shtml",
                      "/pokearth/hoenn/3rd/route102.shtml",
                      "/pokearth/hoenn/3rd/route103.shtml",
                      "/pokearth/hoenn/3rd/route104.shtml",
                      "/pokearth/hoenn/3rd/route105.shtml",
                      "/pokearth/hoenn/3rd/route106.shtml",
                      "/pokearth/hoenn/3rd/route107.shtml",
                      "/pokearth/hoenn/3rd/route108.shtml",
                      "/pokearth/hoenn/3rd/route109.shtml",
                      "/pokearth/hoenn/3rd/route110.shtml",
                      "/pokearth/hoenn/3rd/route111.shtml",
                      "/pokearth/hoenn/3rd/route112.shtml",
                      "/pokearth/hoenn/3rd/route113.shtml",
                      "/pokearth/hoenn/3rd/route114.shtml",
                      "/pokearth/hoenn/3rd/route115.shtml",
                      "/pokearth/hoenn/3rd/route116.shtml",
                      "/pokearth/hoenn/3rd/route117.shtml",
                      "/pokearth/hoenn/3rd/route118.shtml",
                      "/pokearth/hoenn/3rd/route119.shtml",
                      "/pokearth/hoenn/3rd/route120.shtml",
                      "/pokearth/hoenn/3rd/route121.shtml",
                      "/pokearth/hoenn/3rd/route122.shtml",
                      "/pokearth/hoenn/3rd/route123.shtml",
                      "/pokearth/hoenn/3rd/route124.shtml",
                      "/pokearth/hoenn/3rd/route125.shtml",
                      "/pokearth/hoenn/3rd/route126.shtml",
                      "/pokearth/hoenn/3rd/route127.shtml",
                      "/pokearth/hoenn/3rd/route128.shtml",
                      "/pokearth/hoenn/3rd/route129.shtml",
                      "/pokearth/hoenn/3rd/route130.shtml",
                      "/pokearth/hoenn/3rd/route131.shtml",
                      "/pokearth/hoenn/3rd/route132.shtml",
                      "/pokearth/hoenn/3rd/route133.shtml",
                      "/pokearth/hoenn/3rd/route134.shtml",
                      "/pokearth/hoenn/3rd/abandonedship.shtml",
                      "/pokearth/hoenn/3rd/alteringcave.shtml",
                      "/pokearth/hoenn/3rd/aquahideout.shtml",
                      "/pokearth/hoenn/3rd/artisancave.shtml",
                      "/pokearth/hoenn/3rd/battlefrontier.shtml",
                      "/pokearth/hoenn/3rd/battleresort.shtml",
                      "/pokearth/hoenn/3rd/battletower.shtml",
                      "/pokearth/hoenn/3rd/birthisland.shtml",
                      "/pokearth/hoenn/3rd/caveoforigin.shtml",
                      "/pokearth/hoenn/3rd/crescentisle.shtml",
                      "/pokearth/hoenn/3rd/desertunderpass.shtml",
                      "/pokearth/hoenn/3rd/dewfordtown.shtml",
                      "/pokearth/hoenn/3rd/evergrandecity.shtml",
                      "/pokearth/hoenn/3rd/fabledcave.shtml",
                      "/pokearth/hoenn/3rd/fallarbortown.shtml",
                      "/pokearth/hoenn/3rd/farawayisland.shtml",
                      "/pokearth/hoenn/3rd/fierypath.shtml",
                      "/pokearth/hoenn/3rd/fortreecity.shtml",
                      "/pokearth/hoenn/3rd/gnarledden.shtml",
                      "/pokearth/hoenn/3rd/granitecave.shtml",
                      "/pokearth/hoenn/3rd/jaggedpass.shtml",
                      "/pokearth/hoenn/3rd/lavaridgetown.shtml",
                      "/pokearth/hoenn/3rd/lilycovecity.shtml",
                      "/pokearth/hoenn/3rd/littleroottown.shtml",
                      "/pokearth/hoenn/3rd/magmahideout.shtml",
                      "/pokearth/hoenn/3rd/marinecave.shtml",
                      "/pokearth/hoenn/3rd/mauvillecity.shtml",
                      "/pokearth/hoenn/3rd/meteorfalls.shtml",
                      "/pokearth/hoenn/3rd/miragecave.shtml",
                      "/pokearth/hoenn/3rd/mirageforest.shtml",
                      "/pokearth/hoenn/3rd/mirageisland.shtml",
                      "/pokearth/hoenn/3rd/miragemountain.shtml",
                      "/pokearth/hoenn/3rd/miragetower.shtml",
                      "/pokearth/hoenn/3rd/mossdeepcity.shtml",
                      "/pokearth/hoenn/3rd/mt.chimney.shtml",
                      "/pokearth/hoenn/3rd/mt.pyre.shtml",
                      "/pokearth/hoenn/3rd/navelrock.shtml",
                      "/pokearth/hoenn/3rd/namelesscavern.shtml",
                      "/pokearth/hoenn/3rd/newmauville.shtml",
                      "/pokearth/hoenn/3rd/oldaletown.shtml",
                      "/pokearth/hoenn/3rd/pacifidlogtown.shtml",
                      "/pokearth/hoenn/3rd/pathlessplain.shtml",
                      "/pokearth/hoenn/3rd/petalburgcity.shtml",
                      "/pokearth/hoenn/3rd/petalburgwoods.shtml",
                      "/pokearth/hoenn/3rd/pokemonleague.shtml",
                      "/pokearth/hoenn/3rd/rustborocity.shtml",
                      "/pokearth/hoenn/3rd/rusturftunnel.shtml",
                      "/pokearth/hoenn/3rd/safarizone.shtml",
                      "/pokearth/hoenn/3rd/scorchedslab.shtml",
                      "/pokearth/hoenn/3rd/seamauville.shtml",
                      "/pokearth/hoenn/3rd/seafloorcavern.shtml",
                      "/pokearth/hoenn/3rd/sealedchamber.shtml",
                      "/pokearth/hoenn/3rd/secretislet.shtml",
                      "/pokearth/hoenn/3rd/secretmeadow.shtml",
                      "/pokearth/hoenn/3rd/secretshore.shtml",
                      "/pokearth/hoenn/3rd/shoalcave.shtml",
                      "/pokearth/hoenn/3rd/skypillar.shtml",
                      "/pokearth/hoenn/3rd/slateportcity.shtml",
                      "/pokearth/hoenn/3rd/soaringinthesky.shtml",
                      "/pokearth/hoenn/3rd/sootopoliscity.shtml",
                      "/pokearth/hoenn/3rd/southernisland.shtml",
                      "/pokearth/hoenn/3rd/sstidal.shtml",
                      "/pokearth/hoenn/3rd/terracave.shtml",
                      "/pokearth/hoenn/3rd/tracklessforest.shtml",
                      "/pokearth/hoenn/3rd/trainerhill.shtml",
                      "/pokearth/hoenn/3rd/verdanturftown.shtml",
                      "/pokearth/hoenn/3rd/victoryroad.shtml",
                      ]
        }

        self.game_map = {
            "Pokémon Red": "red",
            "Pokémon Blue": "blue",
            "Pokémon Green": "green",
            "Pokémon Blue (Jp.)": "blue_jp",
            "Pokémon Yellow": "yellow",
            "Pokémon Gold": "gold",
            "Pokémon Silver": "silver",
            "Pokémon Crystal": "crystal",
            "Pokémon Ruby": "ruby",
            "Pokémon Sapphire": "sapphire",
            "Pokémon Emerald": "emerald"
        }

        self.type_tags = {"Standard Walking", "Old Rod", "Good Rod", "Super Rod", "Radio Pokémon", "Headbutt Pokémon",
                          "Hordes", "Interactable Pokémon", "PokéRadar", "GBA Insertion",  "Swarm", "Honey Tree", "Surf", "Headbutt - Special Trees",
                          "Surfing", "Fishing - Old Rod", "Fishing - Good Rod", "Fishing - Super Rod", "Rock Smash",
                          "Gift Pokémon", }

        self.tod_tags = {"Morning", "Day", "Night"}

    def get_route_data(self):
        self.master_dict = {}
        gen_key = "gen_3"

        for suf_url in self.gen_url_map[gen_key]:
            url = urllib.parse.urljoin(self.pre_url, suf_url)

            route = os.path.basename(suf_url)[:-6]
            route = re.sub("[^A-Za-z0-9_-]", "", route)
            route_data = self.get_route_data_from_website(url)

            route = self.gen_route_changes_map[gen_key].get(route, route)
            print(url, route)

            for gen, gen_data in route_data.items():
                self.master_dict.setdefault(gen, {})
                self.master_dict[gen].setdefault(route, {})

                self.master_dict[gen][route] = gen_data | self.master_dict[gen][route]
            #pprint.pprint(route_data)

        #pprint.pprint(self.master_dict)






    def get_route_data_from_website(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        #with open("test.txt", "r", encoding="utf8") as f:
         #   data = f.read()

        #soup = BeautifulSoup(data, 'html.parser')

        route_master = {}

        encounter_tables = soup.find_all("table", {"class": ["extradextable", "dextable"]})
        current_type = None
        current_tod = None
        current_games = []

        for table in encounter_tables:
            trs = table.find_all("tr")

            i = 0
            current_tr = trs[i]


            text = current_tr.text.strip()
            if text in self.type_tags or text.startswith("Gift -"):
                current_type = text

                i += 1

                # This would break on https://www.serebii.net/pokearth/johto/2nd/olivinecity.shtml if not there
                if i == len(trs):
                    continue

                current_tr = trs[i]
                if text.startswith("Gift -") or text.startswith("Trade - "):
                    text = re.sub(".* - ", "Pokémon ", text).strip()
                else:

                    text = current_tr.text.strip()

            #text_spl = re.split(",|\/|&", text)
            text_spl = text.split("/")
            temp_games = []
            for text in text_spl:
                text = text.strip()
                if text in self.game_map:
                    temp_games.append(self.game_map[text])
                    route_master.setdefault(self.game_map[text], {})

            if len(temp_games):
                current_games = temp_games
                i += 1
                current_tr = trs[i]

            text = current_tr.text.strip()
            #print(text, self.tod_tags, text in self.tod_tags, i, current_tr)
            if text in self.tod_tags:
                current_tod = text
                i += 1
                current_tr = trs[i]
                text = current_tr.text.strip()

            name_elements = table.find_all("td", {"class": "name"})
            type_elements = table.find_all("td", {"class": "type"})
            rate_elements = table.find_all("td", {"class": "rate"}) if current_type not in {"Interactable Pokémon"} else [None for i in range(len(name_elements))]
            level_elements = table.find_all("td", {"class": "level"})
            for name_element, type_element, rate_element, level_element in zip(name_elements,
                                                                               type_elements,
                                                                               rate_elements,
                                                                               level_elements):
                pokemon_name = re.sub("[^A-Za-z0-9-_]", "", name_element.text.strip()).lower()

                types = []
                for img in type_element.find_all("img"):
                    types.append(os.path.basename(img["src"])[:-4])
                for game in current_games:
                    route_master[game].setdefault(pokemon_name, [])
                    route_master[game][pokemon_name].append({
                       #  "types": types,
                        "rate": rate_element.text.strip() if current_type not in {"Interactable Pokémon"} else None,
                        "level": level_element.text.strip(),
                        "method": current_type,
                        "tod": current_tod
                    })

        #pprint.pprint(route_master)
        return route_master


if __name__ == "__main__":
    spa = SerebiiPokearthAdapter("test")
    spa.get_route_data()
    spa.save_data()
    #spa.get_route_data_from_website("TEST")
