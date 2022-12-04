import json

class PokemonGameDataAdapter:
    def __init__(self, game_data_path):
        self.master_dict = {}
        self.game_data_path = game_data_path

    def get_route_data(self):
        print("IMPLEMENT ME")

    def get_pokemon_data(self):
        print("IMPLEMENT ME")

    def save_data(self):
        for game_key, game_location_data in self.master_dict.items():
            file_name = "../resources/route_encounter_data/route_encounter_%s.json" % game_key
            with open(file_name, "w") as f:
                json.dump(game_location_data, f)
