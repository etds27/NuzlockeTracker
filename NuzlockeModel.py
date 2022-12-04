import os
import pprint
import re
import json

SPRITE_ROOT_DIR = "resources\\sprites"

model_options = {
    "menu_sprite_images":
        ['ani_pinball.gif',
         'ico-a_gb.gif',
         'ico-a_gbc.gif',
         'ico_3ds.png',
         'ico_old.png',
         'o_hgss.png',
         ],
    "battle_sprite_images":
        ['art-hd_anime',
         'art_1-green',
         'art_1-rb',
         'art_dream-world',
         'art_global-link',
         'ken-sugimori',
         'spr_3ds',
         'spr_black-white',
         'spr_crystal',
         'spr_diamond-pearl',
         'spr_emerald',
         'spr_firered-leafgreen',
         'spr_gold',
         'spr_green_gb',
         'spr_green_supergb',
         'spr_hgss',
         'spr_platinum',
         'spr_red-blue_gb',
         'spr_red-blue_supergb',
         'spr_ruby-sapphire',
         'spr_silver',
         'spr_yellow_gb',
         'spr_yellow_gbc',
         'spr_yellow_supergb'],
    "pokemon_data": [f.replace(".json", "") for f in os.listdir("resources/pokemon_data")],
    "map_location_data": [f.replace(".json", "") for f in os.listdir("resources/map_location_data")],
    "map_image": [f.replace(".json", "") for f in os.listdir("resources/map_images")],
    "route_encounter_data": [f.replace(".json", "") for f in os.listdir("resources/route_encounter_data")],
}
"""
menu options:

    
battle options:
    
"""

gen_map = {
    "red": {
        "menu": "ico-a_gb",
        "battle": "spr_red-blue_supergb",
        "location_encounter_data": "route_encounter_red",
        "location_geometry_data": "map_location_data_kanto_gen_1",
        "map_image": "kanto_gen_1.png",
        "pokemon_data": "gen_1"},
    "blue": {
        "menu": "ico-a_gb",
        "battle": "art_1-rb",
        "location_encounter_data": "route_encounter_red",
        "location_geometry_data": "map_location_data_kanto_gen_1",
        "map_image": "kanto_gen_1.png",
        "pokemon_data": "gen_1"},
    "gold": {
        "menu": "ico-a_gbc",
        "battle": "spr_emerald",
        "location_encounter_data": "route_encounter_gold",
        "location_geometry_data": "map_location_data_johto_kanto_gen_2",
        "map_image": "johto_kanto_gen_2.png",
        "pokemon_data": "gen_2"
    },
    "silver": {
        "menu": "ico-a_gbc",
        "battle": "spr_silver",
        "location_encounter_data": "route_encounter_silver",
        "location_geometry_data": "map_location_data_johto_kanto_gen_2",
        "map_image": "johto_kanto_gen_2.png",
        "pokemon_data": "gen_2"
    },
    "crystal": {
        "menu": "ico-a_gbc",
        "battle": "spr_crystal",
        "location_encounter_data": "route_encounter_crystal",
        "location_geometry_data": "map_location_data_johto_kanto_gen_2",
        "map_image": "johto_kanto_gen_2.png",
        "pokemon_data": "gen_2"
    },
    "ruby": {
        "menu": "ico_old",
        "battle": "spr_ruby-sapphire",
        "location_encounter_data": "route_encounter_ruby",
        "location_geometry_data": "map_location_data_hoenn_gen_3",
        "map_image": "hoenn_gen_3.png",
        "pokemon_data": "gen_3"
    },
    "sapphire": {
        "menu": "ico_old",
        "battle": "spr_ruby-sapphire",
        "location_encounter_data": "route_encounter_sapphire",
        "location_geometry_data": "map_location_data_hoenn_gen_3",
        "map_image": "hoenn_gen_3.png",
        "pokemon_data": "gen_3"
    },
    "emerald": {
        "menu": "ico-a_gbc",
        "battle": "art_1-rb",
        "location_encounter_data": "route_encounter_emerald",
        "location_geometry_data": "map_location_data_hoenn_gen_3",
        "map_image": "hoenn_gen_3.png",
        "pokemon_data": "gen_3"
    },
}


class NuzlockeModel:
    def __init__(self, game_key="red"):

        self.game_key = game_key

        self.location_data = {}
        self.location_encounter_data = {}
        self.pokemon_data = {}

        self.master = {}
        self.load_encounter_data()
        self.load_location_data()
        self.load_pokemon_data()

        self.create_master()
        """for key in self.location_data.keys():
            self.master[key] = {"pokemon": None,
                                "deaths": [],
                                "available_pokemon": random.sample(pokemon_151, k=random.randint(1, 10)),
                                "display_name": self.location_data[key]["display_name"]}"""

        # self.master["pallettown"]["pokemon"] = "charmander"
        # self.master["route_3"]["pokemon"] = "grimer"

    def load_location_data(self):
        with open("resources/map_location_data/%s.json" % gen_map[self.game_key]["location_geometry_data"], "r") as f:
            self.location_data = json.load(f)

    def load_encounter_data(self):
        with open("resources/route_encounter_data/%s.json" % gen_map[self.game_key]["location_encounter_data"],
                  "r") as f:
            self.location_encounter_data = json.load(f)

    def load_pokemon_data(self):
        with open("resources/pokemon_data/%s.json" % gen_map[self.game_key]["pokemon_data"], "r") as f:
            self.pokemon_data = json.load(f)

    def create_master(self):
        for route_name in self.location_data.keys():
            self.master[route_name] = {
                "pokemon": None,
                "death": None,
                "available_pokemon": self.location_encounter_data.get(route_name, {}).keys(),
                "display_name": self.location_data[route_name]["display_name"]
            }

    def update_pokemon_on_location(self, pokemon, location):
        """
        Updates the pokemon at a specific location in the model
        :param pokemon:
        :param location:
        :return:
        """
        if pokemon is not None:
            self.master[location]["pokemon"] = pokemon
            self.master[location]["available_pokemon"] = []
        else:
            self.master[location]["pokemon"] = None
            self.master[location]["available_pokemon"] = []  # Update this to default pokemon after resetting

    def get_data_for_poi(self, location=None):
        if location:
            return self.master[location]
        else:
            return self.master

    def get_map_location_data(self, location=None):
        if location:
            return self.location_data[location]
        else:
            return self.location_data

    def get_pokemon_sprite_paths(self, pokemon, game_key):
        """

        :param pokemon:
        :param game_key:
        :return:
        """

        pokemon_dir = "%03i_%s" % (self.pokemon_data[pokemon]['number'], pokemon)

        battle_path = os.path.join(SPRITE_ROOT_DIR, pokemon_dir, "battle")
        battle_key = gen_map[game_key]["battle"]

        ext_search = re.search("(\.[a-z0-9]{2,3})$", battle_key)

        battle_ext = ext_search.group(1) if ext_search else None

        menu_path = os.path.join(SPRITE_ROOT_DIR, pokemon_dir, "menu")
        menu_key = gen_map[game_key]["menu"]
        ext_search = re.search("(\.[a-z0-9]{2,3})$", menu_key)
        menu_ext = ext_search.group(1) if ext_search else None

        if not battle_ext:
            for filename in os.listdir(battle_path):
                ret = re.match("^%s\.([a-zA-Z]+)" % battle_key, filename)
                if ret:
                    battle_ext = ret.group(1)
                    break

        if not menu_ext:
            for filename in os.listdir(menu_path):
                ret = re.match("^%s\.([a-zA-Z]+)" % menu_key, filename)
                if ret:
                    menu_ext = ret.group(1)
                    break

        battle_path = os.path.join(battle_path, "{}.{}".format(battle_key, battle_ext))
        menu_path = os.path.join(menu_path, "{}.{}".format(menu_key, menu_ext))

        battle_path = battle_path if os.path.exists(battle_path) else "resources/sprites/000_missingno/missingno.png"
        menu_path = menu_path if os.path.exists(menu_path) else "resources/sprites/000_missingno/missingno.png"
        return battle_path, menu_path

    def get_map_image_path(self, game_key):
        return os.path.join("resources/map_images", gen_map[game_key]["map_image"])

    def get_pokemon_for_location(self, location):
        return self.master[location]["pokemon"]

    def set_pokemon_for_location(self, pokemon, location):
        self.master[location]["pokemon"] = pokemon

    def get_pokemon_data(self, pokemon):
        return self.pokemon_data[pokemon]

    def get_pokemons_data(self, pokemons):
        return {pokemon: self.get_pokemon_data(pokemon) for pokemon in pokemons}

    def get_model_settings(self, game_key, key=None):
        if key:
            return gen_map[game_key][key]
        else:
            return gen_map[game_key]

    def set_model_setting(self, gen_key, kvs):
        for k, v in kvs:
            gen_map[gen_key][k] = v

    def get_model_options(self, key=None):
        if key:
            return model_options[key]
        else:
            return model_options


if __name__ == "__main__":
    nm = NuzlockeModel()
    print(nm.get_pokemon_sprite_paths("pikachu", "red"))
