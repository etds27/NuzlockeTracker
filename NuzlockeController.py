import enum
import logging
import random
import tkinter as tk

import NuzlockeDisplay
import NuzlockeModel

logging.basicConfig(level=logging.INFO)


class OverlayType(enum.Enum):
    NONE = 0,
    AVAILABLE_POKEMON = 1,
    SEARCH = 2


class NuzlockeController:
    def __init__(self, win: tk.Tk, game="red"):

        self.game_key = game
        self.model = NuzlockeModel.NuzlockeModel(game_key=game)
        self.map_display = NuzlockeDisplay.NuzlockeMapDisplay(self, win)
        self.map_display.pack(side='left', expand=False, fill='both')

        self.location_readout = NuzlockeDisplay.NuzlockeLocationReadout(self, win)
        self.location_readout.pack(side='left', expand=True, fill='both')

        self.current_overlay_key = OverlayType.NONE
        self.current_overlay_locations = set([])
        self.current_overlay_status = False
        self.redisplay_overlay_on_location_deselect = False

        self.selected_location_key = None
        self.selected_pokemon_key = None

        # print(self.map_display.image.width(), "D", self.map_display.height())
        win.geometry("%ix%i+0+0" % (self.map_display.image.width() + 400, self.map_display.image.height() + 30))
        win.bind("<Return>", self.toggle_route_status_overlay)
        win.bind("<Escape>", lambda event, lk=self.get_selected_location(): self.location_deselect(lk))

    def toggle_route_status_overlay(self, *args):
        if self.get_selected_location() is not None:
            return

        # self.current_overlay_key = OverlayType.AVAILABLE_POKEMON
        self.current_overlay_status = not self.current_overlay_status
        logging.debug(
            "NuzlockeController.toggle_route_status_overlay: current_overlay_key: %s | current_overlay_status: %s" % (
                self.current_overlay_key, self.current_overlay_status))

        if self.current_overlay_status:
            self.current_overlay_key = OverlayType.AVAILABLE_POKEMON if self.current_overlay_key is OverlayType.SEARCH else OverlayType.SEARCH
            self.display_current_overlay()
        else:
            self.remove_overlay()

    def display_current_overlay(self, *args):
        if self.current_overlay_key == OverlayType.AVAILABLE_POKEMON:
            self.display_available_pokemon_overlay()
        elif self.current_overlay_key == OverlayType.SEARCH:
            self.display_search_overlay({
                "search_type": "pokemon_name",
                "search_term": "pidgey",
                "include_unavailable_locations": False
            })

    def display_available_pokemon_overlay(self):
        location_data = self.model.get_map_location_data()

        for route, route_data in location_data.items():
            d = route_data | self.model.get_data_for_poi(route)
            if d["pokemon"] is None:
                self.map_display.display_available_route_overlay(route, d["rectangles"])
            else:
                battle_sprite_path, menu_sprite_path = self.get_pokemon_sprite_paths(d["pokemon"])

                if random.random() > 0.5:
                    self.map_display.display_taken_route_overlay(route, d["rectangles"], menu_sprite_path)
                else:
                    self.map_display.display_dead_route_overlay(route, d["rectangles"], menu_sprite_path)

            self.current_overlay_locations.add(route)

    def display_search_overlay(self, search_params):
        """
        {
            search_type: "pokemon_name" | "types"
            search_term: pokemon_name: Str | types: List
            include_unvailable_locations: bool
        }
        :param search_params:
        :return:
        """
        routes = []

        if search_params["search_type"] == "pokemon_name":
            _, sprite_path = self.get_pokemon_sprite_paths(search_params["search_term"])
            for route, route_data in self.model.get_map_location_data().items():
                d = route_data | self.model.get_data_for_poi(route)

                if not search_params["include_unavailable_locations"] and d["pokemon"] is not None:
                    continue

                if search_params["search_term"] in d["available_pokemon"]:
                    self.current_overlay_locations.add(route)
                    self.map_display.display_search_result_overlay(route,
                                                                   d["rectangles"],
                                                                   sprite_path)
                    continue

        if search_params["search_type"] == "types":
            for route, route_data in self.model.get_map_location_data():
                d = route_data | self.model.get_data_for_poi(route)

                pass

    def remove_overlay(self, *args):
        for location_name in self.current_overlay_locations:
            self.map_display.remove_single_location_overlay(location_name)
        self.current_overlay_locations.clear()

    def sort_pokemon_list(self, pokemon_list, key="number", reverse=False):
        pokemon_data = self.model.get_pokemons_data(pokemon_list)
        return [name for name, data in sorted(pokemon_data.items(), key=lambda d: d[1][key], reverse=reverse)]

    def on_location_enter(self, location):
        """
        When the operator hovers over a POI, get the current status of the pokemon from that place
        Display the available pokemon in the area
        :param location:
        :return:
        """
        location_data = self.model.get_data_for_poi(location)
        location_data["available_pokemon"] = self.sort_pokemon_list(location_data["available_pokemon"], "number")

        self.map_display.location_preselect(location, location_data["display_name"], location_data["pokemon"])

        if location_data["pokemon"]:
            self.map_display.populate_banner(location_data["display_name"], self.get_pokemon_name(pokemon_key=location_data["pokemon"]))
        else:
            self.map_display.populate_banner(location_data["display_name"])

        if self.selected_location_key is None:
            self.location_readout.display_location(location_data)

    def on_location_exit(self, location):
        self.map_display.location_depreselect()
        if self.selected_location_key is None:
            self.location_readout.clear()

    def location_select(self, location):
        if self.selected_location_key is None:
            self.map_display.deselect_location()

        self.selected_location_key = location
        location_data = self.model.get_data_for_poi(location)

        location_data["available_pokemon"] = self.sort_pokemon_list(location_data["available_pokemon"], "number")

        self.selected_pokemon_key = location_data["pokemon"]
        if self.selected_pokemon_key:
            self.map_display.populate_banner(location_data["display_name"], self.get_pokemon_name(pokemon_key=self.selected_pokemon_key))
        else:
            self.map_display.populate_banner(location_data["display_name"])

        self.location_readout.clear()
        self.location_readout.display_location(location_data)

        if self.current_overlay_status:
            self.remove_overlay()
            self.redisplay_overlay_on_location_deselect = True
        else:
            self.redisplay_overlay_on_location_deselect = False

        self.map_display.select_location(location)

    def location_deselect(self, location):
        self.map_display.deselect_location()
        self.location_readout.clear()
        self.selected_location_key = None

        self.map_display.depopulate_banner()


        if self.redisplay_overlay_on_location_deselect:
            self.display_current_overlay()

    def on_location_click(self, location):
        if location == self.selected_location_key:
            self.location_deselect(location)
            return
        else:
            if self.selected_location_key is not None:
                self.location_deselect(self.selected_location_key)
            self.location_select(location)

            # return data["pokemon"], data["available_pokemon"], data["deaths"]

    def on_available_pokemon_click(self, pokemon):
        if pokemon == self.model.get_pokemon_for_location(self.selected_location_key):
            self.unset_selected_pokemon()
        else:
            self.set_selected_pokemon(pokemon)

    def on_available_pokemon_enter(self, pokemon):
        if pokemon == self.selected_pokemon_key:
            return
        self.location_readout.preselect_available_pokemon(pokemon)

    def on_available_pokemon_leave(self, pokemon):
        if pokemon == self.selected_pokemon_key:
            return
        self.location_readout.depreselect_available_pokemon(pokemon)

    def on_map_click(self):
        if self.selected_location_key is not None:
            self.location_deselect(self.selected_location_key)

    def unset_selected_pokemon(self):
        self.model.set_pokemon_for_location(None, self.selected_location_key)
        self.location_readout.unset_selected_pokemon_display()
        self.map_display.populate_banner(self.selected_location_key, None)
        # self.map_display.on_available_pokemon_deselect()
        self.selected_pokemon_key = None

    def set_selected_pokemon(self, pokemon):
        self.model.set_pokemon_for_location(pokemon, self.selected_location_key)
        self.location_readout.set_selected_pokemon_display(pokemon)
        self.map_display.populate_banner(self.get_map_location_data(self.selected_location_key)["display_name"], self.get_pokemon_name(pokemon))
        self.selected_pokemon_key = pokemon
        # self.map_display.on_available_pokemon_select(pokemon, self.selected_location_key)

    def get_pokemon_sprite_paths(self, pokemon):
        return self.model.get_pokemon_sprite_paths(pokemon, self.game_key)

    def get_map_location_data(self, location=None):
        return self.model.get_map_location_data(location)

    def get_selected_location(self):
        return self.selected_location_key

    def get_pokemon_data(self, pokemon_key):
        return self.model.get_pokemon_data(pokemon_key)

    def get_pokemon_name(self, pokemon_key):
        return self.get_pokemon_data(pokemon_key)["display_name"]

    def get_pokemon_type(self, pokemon_key):
        return self.get_pokemon_data(pokemon_key)["types"]

    def get_map_image_path(self):
        return self.model.get_map_image_path(self.game_key)

    def assemble_dialog_widget_info(self):
        settings = self.get_model_settings()
        options = self.model.get_model_options()

        master = []
        c = 0
        for c, k in enumerate(settings.keys()):
            row = [k, k, options[k], settings[k], c]
            master.append(row)

        master.append(["overlay", "Overlay Type", [s for s in OverlayType], self.current_overlay_key, c + 1])

    def get_model_settings(self):
        return self.model.get_model_settings(self.game_key)

    def set_model_settings(self, key, value):
        self.model.set_model_setting(self.game_key, kvs=[(key, value)])

if __name__ == "__main__":
    win = tk.Tk()
    nc = NuzlockeController(win, game="blue")
    #win.geometry("850x600")

    win.mainloop()
