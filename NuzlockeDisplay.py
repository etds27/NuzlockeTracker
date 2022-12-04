import logging
import tkinter as tk
from PIL import Image, ImageTk

import NuzlockeCanvasItems
import NuzlockeController

SCALE = 3
BOX_W = 8
BOX_H = 8

BATTLE_SPRITE_SCALE = 2
MENU_SPRITE_SCALE = 2
MAX_BATTLE_SPRITE_SIZE = 96
MAX_MENU_SPRITE_SIZE = 40

AVAILABLE_POKEMON_PRESELECT = "#a0a0a0"
AVAILABLE_POKEMON_BG = "#edfcf5"
AVAILABLE_POKEMON_FG = "#000000"

AVAILABLE_POKEMON_PRESELECT_OUTLINE_COLOR = "#a0a0a0"



AVAILABLE_POKEMON_FRAME_THEME = {
    "bg": AVAILABLE_POKEMON_BG,
}

AVAILABLE_POKEMON_THEME = AVAILABLE_POKEMON_FRAME_THEME | {"fg": AVAILABLE_POKEMON_FG, "font": ("Helvetica", "10")}

AVAILABLE_POKEMON_THEME_BOLD = AVAILABLE_POKEMON_THEME | {"font": ("Helvetica", "10", "bold")}

TYPE_COLOR_MAP = {
    "normal": "#A8A77A",
    "fire": "EE8130",
    "water": "#6390F0",
    "electric": "#F7D02C",
    "grass": "#7AC74C",
    "ice": "#96D9D6",
    "fighting": "#C22E28",
    "poison": "#A33EA1",
    "ground": "#E2BF65",
    "flying": "#A98FF3",
    "psychic": "#F95587",
    "bug": "#A6B91A",
    "rock": "#B6A136",
    "ghost": "#735797",
    "dragon": "#6F35FC",
    "dark": "#705746",
    "steel": "#B7B7CE",
    "fairy": "D685GAD"
}


def xywh2xyxy(x, y, w, h):
    return x, y, x + w, y + h


def xywh2coords(x, y, w, h):
    return xyxy2coords(*xywh2xyxy(x, y, w, h))


def xyxy2coords(x1, y1, x2, y2):
    return [(x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)]


def scale(x, y, w, h):
    return x * SCALE, y * SCALE, w * SCALE, h * SCALE


def combineRects(rects):
    print(rects)
    main = list(xywh2coords(*rects[0]))
    print(main)
    for rect in rects[1:]:
        rect = xywh2coords(*rect)
        print(main, rect)
        for i in range(0, len(main) - 1):
            merge = False

            mp1, mp2 = main[i], main[i + 1]

            idx = 0 if mp1[0] == mp2[0] else 1
            i_idx = abs(1 - idx)

            value = mp1[idx]

            if idx == 0:  # x axis:
                direction = -1 if mp2[i_idx] < mp1[i_idx] else 1  # -1 = Down, 1 = Up
            else:  # y axis
                direction = -1 if mp2[i_idx] < mp1[i_idx] else 1

            for j in range(0, len(rect) - 1):
                np1, np2 = rect[j], rect[j + 1]

                print(value, np1[idx], np2[idx])

                # Found a shared border. Now check if other axis is aligned
                if np1[idx] == value and np2[idx] == value:
                    print("Found alignment")
                    print(mp1[i_idx], mp2[i_idx], np1[i_idx], np2[i_idx])

                    # Check if the aligned edge is overlaps with the main line
                    if direction == 1:
                        if np1[i_idx] < mp1[i_idx] and np2[i_idx] < mp1[i_idx] or \
                                np1[i_idx] > mp2[i_idx] and np2[i_idx] > mp2[i_idx]:
                            break

                    merge = True

                    print("Found shared edge %s %s, %s %s" % (mp1, mp2, np1, np2))

                    # if the direction is 1 meaning it was matched on an upward main edge,
                    # Then insert the new rect counter clockwise into the main
                    for c, point in enumerate(rect[j + 1:] + rect[:j]):
                        print("\t instering %s" % str(point))
                        main.insert(i + c + 1, point)
                    break

            # If a merge was made, then skip the rest
            if merge:
                break

        print(main)
    return main


class PokemonMapDisplay(tk.Canvas):
    def __init__(self, controller, *args, **kwargs):
        super(PokemonMapDisplay, self).__init__(highlightthickness=0, *args, **kwargs)

        self.controller: NuzlockeController.NuzlockeController = controller
        self.location_boxes = {}

        self.image_path = self.controller.get_map_image_path()
        self.image = Image.open(self.image_path)
        self.image = self.image.resize((int(self.image.width * SCALE), int(self.image.height * SCALE)))

        self.image = ImageTk.PhotoImage(self.image)

        self.map_id = self.create_image(0, 0, anchor="nw", image=self.image)

        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.configure(background="black")

        self.configure(width=self.image.width())
        self.configure(height=self.image.height())

        self.create_boxes()

        self.addtag_all("all")

    def on_resize(self, event):
        """
        Method to resize all canvas items when the canvas widget size changes
        :param event:
        :return:
        """
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        # self.scale("all", 0, 0, wscale, hscale)

    def create_boxes(self):
        """
        Creates the selection boxes for each POI specified for the map
        :return:
        """
        location_data = self.controller.get_map_location_data()

        for place_name, place_dict in location_data.items():
            rectangles = place_dict["rectangles"]
            points = [i * SCALE for i in self.create_polygon_points_from_rectangles(rectangles)]
            poly = self.create_polygon(*points, outline="", width=0, fill="")

            self.location_boxes[place_name] = poly


    def create_polygon_points_from_rectangles(self, rectangles):
        points = []
        for rectangle in rectangles:
            points += xywh2coords(*rectangle)

        return [i for t in points for i in t]

    def create_location_overlay(self, location_name, location_rect, fill="gray", alpha=0.5):
        """
        Place an overlay (underneath) the route specified.
        An overlay is just a transparentn rectangle that covers the location
        :param location_name:
        :param location_rect:
        :param fill:
        :param alpha:
        :return:
        """
        rect, selected_image, selected_image_id = self.create_transparent_rectangle(*location_rect, fill=fill, alpha=alpha)
        self.itemconfigure(rect, tags=["overlay_location", "overlay_location_%s" % location_name])
        self.itemconfigure(selected_image_id, tags=["overlay_location", "overlay_location_%s" % location_name])

        self.overlay_rects.setdefault(location_name, [])
        self.overlay_rects[location_name].append(selected_image)

        self.move_to_bottom(rect)
        self.move_to_bottom(selected_image_id)

    def create_location_overlay_with_image(self, location_name, location_rect, image_path, fill="gray", alpha=0.5):
        """
        Creates an overlay for the location with an image placed in the center of the rectangle specified
        :param location_name:
        :param location_rect:
        :param image_path:
        :param fill:
        :param alpha:
        :return:
        """
        image = Image.open(image_path)
        dim = min(location_rect[2], location_rect[3], image.width, image.height)
        image = image.resize((dim, dim))
        imagetk = ImageTk.PhotoImage(image)
        image_id = self.create_image(location_rect[0] + location_rect[2] // 2, location_rect[1] + location_rect[3] // 2,
                                     image=imagetk,
                                     tags=["overlay_image_locations", "overlay_image_location_%s" % location_name],
                                     anchor="c")

        self.overlay_images.setdefault(location_name, [])
        self.overlay_images[location_name].append(imagetk)

        self.move_to_bottom(image_id)

        self.create_location_overlay(location_name, location_rect, fill, alpha)


    def remove_single_location_overlay(self, location_name):
        self.delete("overlay_location_%s" % location_name)
        self.delete("overlay_image_location_%s" % location_name)

        if location_name in self.overlay_rects:
            self.overlay_rects.pop(location_name)
        if location_name in self.overlay_images:
            self.overlay_images.pop(location_name)

class NuzlockeMapDisplay(PokemonMapDisplay):
    def __init__(self, *args, **kwargs):
        super(NuzlockeMapDisplay, self).__init__(*args, **kwargs)

        self.current_pokemon_banner = None
        self.current_location_banner_label =  None
        self.current_pokeon_banner_label = None

        BANNER_W = self.image.width()
        BANNER_H = 30
        BANNER_X = 0
        BANNER_Y = self.image.height()
        BANNER_PADX = 5
        self.create_rectangle(BANNER_X, BANNER_Y, BANNER_X + BANNER_W, BANNER_Y + BANNER_H, fill="darkgray", outline="")
        self.current_location_banner_label = self.create_text(BANNER_X + BANNER_PADX, BANNER_Y + BANNER_H // 2,  text="", anchor="w")
        self.current_pokemon_banner_label = self.create_text(BANNER_X + BANNER_W - BANNER_PADX, BANNER_Y + BANNER_H // 2,  text="", anchor="e")

        self.selected_image = None
        self.selected_rects = []

        self.overlay_rects = {}
        self.overlay_images = {}

        self.displayed_available_pokemon_images = []
        self.displayed_available_pokemon_ids = []

        self.hover_rect_ids = []

        for place_name, id in self.location_boxes.items():
            self.tag_bind(id, "<Enter>", lambda event, p=place_name: self.on_location_enter(location=p), add="+")
            self.tag_bind(id, "<Leave>", lambda event, p=place_name: self.on_location_exit(location=p), add="+")
            self.tag_bind(id, "<Button-1>", lambda event, p=place_name: self.on_location_click(location=p), add="+")

        self.tag_bind(self.map_id, "<Button-1>", self.on_map_click)
        self.tag_bind(self.map_id, "<Enter>", self.depopulate_banner)

    def on_map_click(self, *args):
        self.controller.on_map_click()

    def on_location_click(self, *args, location=""):
        self.controller.on_location_click(location)

    def select_location(self, location):
        location_data = self.controller.get_map_location_data(location)

        for rectangle in location_data["rectangles"]:
            coords = scale(*rectangle)
            self.create_selected_rect(*coords, fill='green', alpha=.5)

    def deselect_location(self):
        for id in self.find_withtag("selected_location"):
            self.delete(id)

        self.selected_rects = []

    def on_location_enter(self, *args, location=""):
        self.controller.on_location_enter(location)

    def location_preselect(self, location, display_name, pokemon=None):
        self.display_location_outline(location)
        self.populate_banner(display_name, pokemon)

    def location_depreselect(self):
        for item in self.gettags("hover_outline"):
            self.delete(item)
        self.depopulate_banner()

    def populate_banner(self, display_name, pokemon=None):
        self.itemconfigure(self.current_pokemon_banner_label, text=pokemon)
        self.itemconfigure(self.current_location_banner_label, text=display_name)

    def depopulate_banner(self, *args):
        self.itemconfigure(self.current_pokemon_banner_label, text="")
        self.itemconfigure(self.current_location_banner_label, text="")

    def display_location_outline(self, location, width=2):
        location_data = self.controller.get_map_location_data(location)

        for rectangle in location_data["rectangles"]:
            coords = scale(*rectangle)
            rect = self.create_rectangle(coords[0], coords[1], coords[0] + coords[2], coords[1] + coords[3],
                                         fill="", width=width, tags="hover_outline")
            self.hover_rect_ids.append(rect)

        self.tag_raise(self.location_boxes[location])

    def hide_location_outline(self):
        for item in self.gettags("hover_outline"):
            self.delete(item)

    def on_location_exit(self, *args, location=""):
        self.controller.on_location_exit(location)

    def create_selected_rect(self, x, y, w, h, **kwargs):
        rect, selected_image, selected_image_id = self.create_transparent_rectangle(x, y, w, h, width=2, **kwargs)
        self.itemconfigure(rect, tags="selected_location")
        self.itemconfigure(selected_image_id, tags="selected_location")
        self.selected_rects.append(selected_image)

        self.move_to_bottom(rect)
        self.move_to_bottom((selected_image_id))

        return rect, selected_image, selected_image_id

    def hide_selected_rect(self):
        pass

    def create_transparent_rectangle(self, x, y, w, h, **kwargs):
        selected_image = None
        selected_image_id = None

        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = self.winfo_rgb(fill) + (alpha,)
            image = Image.new('RGBA', (w, h), fill)
            selected_image = ImageTk.PhotoImage(image)
            selected_image_id = self.create_image(x, y, image=selected_image, anchor='nw')
        rect = self.create_rectangle(x, y, x + w, y + h, fill="", **kwargs)

        return rect, selected_image, selected_image_id

    def display_taken_route_overlay(self, location_name, location_rects, sprite_path):
        for location_rect in location_rects:
            scaled_rect = scale(*location_rect)

            self.create_location_overlay_with_image(
                location_name,
                scaled_rect,
                sprite_path,
                fill="black",
                alpha=0.5
            )


    def display_dead_route_overlay(self, location_name, location_rects, sprite_path):
        for location_rect in location_rects:
            scaled_rect = scale(*location_rect)

            self.create_location_overlay_with_image(
                location_name,
                scaled_rect,
                sprite_path,
                fill="red",
                alpha=0.5
            )
    def display_available_route_overlay(self, location_name, location_rects):
        for location_rect in location_rects:
            scaled_rect = scale(*location_rect)
            # scaled_rect = xywh2xyxy(*location_rect)

            self.create_location_overlay(location_name, scaled_rect, fill="green", alpha=0.7)

    def display_search_result_overlay(self, location_name, location_rects, sprite_path):
        for location_rect in location_rects:
            scaled_rect = scale(*location_rect)

            self.create_location_overlay_with_image(
                location_name,
                scaled_rect,
                sprite_path,
                fill="cyan",
                alpha=0.5
            )

    def move_to_bottom(self, id):
        self.lower(id)
        self.lift(id, self.map_id)

class NuzlockeLocationReadout(tk.Frame):
    def __init__(self, controller, *args, **kwargs):
        super(NuzlockeLocationReadout, self).__init__(*args, **kwargs)

        self.controller = controller
        self.location_info_panel = tk.Frame(self, **AVAILABLE_POKEMON_FRAME_THEME)
        self.location_label = None
        self.location_variable = tk.StringVar(self)

        self.pokemon_sprite_panel = tk.Frame(self, height=600, **AVAILABLE_POKEMON_FRAME_THEME)
        self.sprite_label = None
        self.pokemon_name_label = None
        self.pokemon_variable = tk.StringVar(self)
        self.pokemon_image = None

        self.available_pokemon_panel = tk.Frame(self, **AVAILABLE_POKEMON_FRAME_THEME)
        self.available_pokemon_label = None
        self.available_pokemon_canvas = tk.Canvas(self.available_pokemon_panel, **AVAILABLE_POKEMON_FRAME_THEME, borderwidth=0)
        #self.available_pokemon_canvas = tk.Canvas(self.available_pokemon_panel, bg="blue", borderwidth=0)
        self.available_pokemon_internal_frame = tk.Frame(self.available_pokemon_canvas, **AVAILABLE_POKEMON_FRAME_THEME, width=222)
        self.available_pokemon_scrollbar = tk.Scrollbar(self.available_pokemon_panel, command=self.available_pokemon_canvas.yview)
        self.available_pokemon_internal_frame_id = self.available_pokemon_canvas.create_window((0, 0), window=self.available_pokemon_internal_frame, anchor="nw")

        self.available_pokemon_canvas.configure(yscrollcommand=self.available_pokemon_scrollbar.set)
        self.available_pokemon_canvas.bind("<Configure>", lambda event: self.on_canvas_configure())
        self.available_pokemon_canvas.bind_all("<MouseWheel>",
                                               lambda event: self.available_pokemon_canvas.yview_scroll(-1*(event.delta//120), "units"))

        self.available_pokemon_canvas.pack(side="left", fill='both', expand=True)
        self.available_pokemon_scrollbar.pack(side="left", fill='y', expand=False)

        self.available_pokemon_table = tk.Frame(self, **AVAILABLE_POKEMON_FRAME_THEME)
        self.available_pokemon_images = []
        self.available_pokemon_row_outline = {}

        self.location_info_panel.grid(row=0, sticky="news")
        self.pokemon_sprite_panel.grid(row=1, sticky="news")
        self.available_pokemon_panel.grid(row=2, sticky="news")

        self.grid_rowconfigure(1, minsize=130)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.create_initial_display()

        self.configure(bg="black")

    def on_canvas_configure(self):
        self.available_pokemon_canvas.itemconfigure(self.available_pokemon_internal_frame_id,
                                                    width=self.available_pokemon_canvas.winfo_width())

        self.available_pokemon_canvas.configure(scrollregion=self.available_pokemon_canvas.bbox('all'))

    def create_initial_display(self):
        self.location_label = tk.Label(self.location_info_panel, textvariable=self.location_variable, **AVAILABLE_POKEMON_THEME_BOLD)
        self.location_label.pack(side="top", expand=True, fill="x")

        self.sprite_label = tk.Label(self.pokemon_sprite_panel, **AVAILABLE_POKEMON_THEME)
        self.pokemon_name_label = tk.Label(self.pokemon_sprite_panel, textvariable=self.pokemon_variable, **AVAILABLE_POKEMON_THEME_BOLD)
        self.sprite_label.pack(side="top", expand=True, fill=None)
        self.pokemon_name_label.pack(side="top", expand=False, fill="x")


    def create_available_pokemon(self, row, pokemon, levels, tod):
        types = self.controller.get_pokemon_type(pokemon)
        name = self.controller.get_pokemon_name(pokemon)

        outline_width = 2
        outline = tk.Frame(self.available_pokemon_internal_frame, **AVAILABLE_POKEMON_FRAME_THEME)
        outline.grid(row=row, column=0, columnspan=4, ipadx=outline_width, ipady=outline_width, sticky="news")

        self.available_pokemon_row_outline[pokemon] = outline

        _, sprite_path = self.controller.get_pokemon_sprite_paths(pokemon)
        image = Image.open(sprite_path)
        iw, ih = min(MAX_MENU_SPRITE_SIZE, image.width * MENU_SPRITE_SCALE), min(MAX_MENU_SPRITE_SIZE, image.height * MENU_SPRITE_SCALE)
        image = image.resize((iw, ih))
        imagetk = ImageTk.PhotoImage(image)
        self.available_pokemon_images.append(imagetk)

        sprite_label = tk.Label(self.available_pokemon_internal_frame, image=imagetk, **AVAILABLE_POKEMON_THEME)
        sprite_label.grid(row=row, column=0, sticky="news", padx=[outline_width, 0], pady=outline_width)

        name_label = tk.Label(self.available_pokemon_internal_frame, text=name, anchor="w", **AVAILABLE_POKEMON_THEME)
        name_label.grid(row=row, column=1, sticky="news", pady=outline_width, padx=[0, 2])

        level_label = tk.Label(self.available_pokemon_internal_frame, text=levels, **AVAILABLE_POKEMON_THEME)
        # level_label.grid(row=row, column=2, sticky="news", pady=outline_width)

        tod_label = tk.Label(self.available_pokemon_internal_frame, text=tod, **AVAILABLE_POKEMON_THEME)
        # tod_label.grid(row=row, column=3, sticky="news", padx=[0, 2], pady=outline_width)

        for widget in [sprite_label, name_label, level_label, tod_label]:
            widget.bind("<Button-1>", lambda event, p=pokemon: self.on_available_pokemon_click(pokemon))
            widget.bind("<Enter>", lambda event, p=pokemon: self.on_available_pokemon_enter(pokemon))
            widget.bind("<Leave>", lambda event, p=pokemon: self.on_available_pokemon_leave(pokemon, event))

    def on_available_pokemon_enter(self, pokemon):
        self.controller.on_available_pokemon_enter(pokemon)

    def on_available_pokemon_leave(self, pokemon, *args):
        self.controller.on_available_pokemon_leave(pokemon)

    def preselect_available_pokemon(self, pokemon):
        self.available_pokemon_row_outline[pokemon].configure(bg=AVAILABLE_POKEMON_PRESELECT_OUTLINE_COLOR)
        self.available_pokemon_row_outline[pokemon].focus_set()

    def depreselect_available_pokemon(self, pokemon):
        self.available_pokemon_row_outline[pokemon].configure(bg=AVAILABLE_POKEMON_BG)


    def clear(self):
        self.location_variable.set("")

        self.unset_selected_pokemon_display()

        self.available_pokemon_images = []

        self.available_pokemon_row_outline = {}

        for widget in self.available_pokemon_internal_frame.winfo_children():
            widget.destroy()


    def display_location(self, location_data):
        logging.info("NuzlockeLocationReadout.display_location: %s" % location_data["display_name"])
        self.location_variable.set(location_data["display_name"])



        self.create_available_pokemon_header()
        for i, available_pokemon in enumerate(location_data["available_pokemon"]):
            self.create_available_pokemon(i + 2, available_pokemon, "50-60", "night")

        self.available_pokemon_panel.rowconfigure("all", uniform=True, minsize=MAX_MENU_SPRITE_SIZE)
        self.available_pokemon_panel.columnconfigure(1, weight=1)

        if location_data["pokemon"] is not None:
            self.set_selected_pokemon_display(location_data["pokemon"])

        self.available_pokemon_internal_frame.grid_columnconfigure(1, weight=1)

        self.available_pokemon_canvas.event_generate("<Configure>")
        self.available_pokemon_canvas.yview_moveto(0)

        self.available_pokemon_internal_frame.rowconfigure("all", uniform=True)
        pass

    def create_available_pokemon_header(self):
        self.available_pokemon_label = tk.Label(self.available_pokemon_internal_frame, text="Available Pokemon:", **AVAILABLE_POKEMON_THEME_BOLD)
        self.available_pokemon_label.grid(row=0, column=0, columnspan=3, sticky="sw")

        sprite_label = tk.Label(self.available_pokemon_internal_frame, text="Sprite", **AVAILABLE_POKEMON_THEME_BOLD)
        name_label = tk.Label(self.available_pokemon_internal_frame, text="Name", **AVAILABLE_POKEMON_THEME_BOLD)
        #level_label = tk.Label(self.available_pokemon_panel, text="Level", **AVAILABLE_POKEMON_THEME_BOLD)
        #tod_label = tk.Label(self.available_pokemon_panel, text="ToD", **AVAILABLE_POKEMON_THEME_BOLD)

        for i, widget in enumerate([sprite_label, name_label]): #  level_label, tod_label]):
            widget.grid(row=1, column=i)

    def on_available_pokemon_click(self, pokemon):
        self.controller.on_available_pokemon_click(pokemon)

    def set_selected_pokemon_display(self, pokemon):
        pokemon_name = self.controller.get_pokemon_name(pokemon)

        battle_sprite_path, _ = self.controller.get_pokemon_sprite_paths(pokemon)

        image = Image.open(battle_sprite_path)
        #iw, ih = min(MAX_BATTLE_SPRITE_SIZE, image.width * BATTLE_SPRITE_SCALE), min(MAX_BATTLE_SPRITE_SIZE, image.height * BATTLE_SPRITE_SCALE)
        iw, ih = MAX_BATTLE_SPRITE_SIZE, MAX_BATTLE_SPRITE_SIZE
        image = image.resize((iw, ih))
        self.pokemon_image = ImageTk.PhotoImage(image)
        self.sprite_label.configure(image=self.pokemon_image, borderwidth=2, relief="solid")

        self.pokemon_variable.set(pokemon_name)


        for outline in self.available_pokemon_row_outline.values():
            outline.configure(bg=AVAILABLE_POKEMON_BG)
        outline = self.available_pokemon_row_outline[pokemon]
        outline.configure(bg="black")



    def unset_selected_pokemon_display(self):
        self.sprite_label.configure(image="")
        self.sprite_label.configure(borderwidth=0, relief=None)
        self.pokemon_image = None
        self.pokemon_variable.set("")


        for outline in self.available_pokemon_row_outline.values():
            outline.configure(bg=AVAILABLE_POKEMON_BG)

class NuzlockeSettingsDialog(tk.Tk):
    def __init__(self):
        super(NuzlockeSettingsDialog, self).__init__()

        self.widget_map = {}

        self.frame = tk.Frame(self)





    def add_dropdown_option(self, dd_key, dd_text, dd_values, dd_start_value=0, row=None):
        label = tk.Label(self.frame, text=dd_text)
        stringvar = tk.StringVar(self)
        stringvar.set(dd_start_value)
        combobox = tk.OptionMenu(self.frame, stringvar, (dd_values))

        self.widget_map[dd_key] = stringvar



if __name__ == "__main__":
    rects = [(1, 1, 2, 2), (3, 1, 2, 3), (5, 0, 1, 4)]
    pts = combineRects(rects)

    win = tk.Tk()
    can = tk.Canvas(win)
    can.pack(fill="both", expand=True)

    r1 = [p * 100 for p in xywh2xyxy(*rects[0])]
    r2 = [p * 100 for p in xywh2xyxy(*rects[1])]

    # can.create_rectangle(*r1, width=1, outline="red", fill="")
    # can.create_rectangle(*r2, width=1, outline='blue', fill="")

    pts = [p * 100 for coord in pts for p in coord]
    can.create_polygon(*pts, width=1, outline="black", fill="")

    win.geometry("600x600")
    win.mainloop()
