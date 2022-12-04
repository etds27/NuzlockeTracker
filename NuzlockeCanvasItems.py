import tkinter

from PIL import Image, ImageTk
import tkinter as tk

import NuzlockeDisplay


def create_available_pokemon_display(canvas, x, y, pokemon, menu_path):
    """
    Create a single available pokemon form at position x, y
    :param canvas:
    :param x:
    :param y:
    :param pokemon:
    :param menu_path:
    :return:
    """
    image = Image.open(menu_path)
    iw = 20
    cols_w = [iw,  # Sprite
              80,  # Pokemon Name
              80]  # Level

    cols_start = [0]
    for i in range(1, len(cols_w)):
        cols_start.append(cols_w[i - 1] + cols_start[i - 1])
    print(cols_start)

    spacing = 3
    h = 30
    w = cols_start[-1] + cols_w[-1]

    print(cols_w)

    mid_y = y + h // 2


    canvas.create_rectangle(x, y, x + w, y + h, fill="white", tags="available_pokemon")

    canvas.displayed_available_pokemon_images.append(ImageTk.PhotoImage(image))

    col = 0
    canvas.create_image(x + (cols_start[col + 1] + spacing) // 2, mid_y, image=canvas.displayed_available_pokemon_images[-1], anchor="c", tags=["available_pokemon", f"available_pokemon_{pokemon}"])

    col += 1
    # canvas.create_line(x + cols_start[col], y, x + cols_start[col], y + h)
    canvas.create_text(x + cols_start[col] + spacing, mid_y, text=pokemon, tags=["available_pokemon", f"available_pokemon_{pokemon}"], anchor="w")

    col += 1
    # canvas.create_line(x + cols_start[col], y, x + cols_start[col], y + h)
    canvas.create_text(x + cols_start[col] + spacing, mid_y, text="45-60", anchor="w", tags=["available_pokemon", f"available_pokemon_{pokemon}"])

    canvas.tag_bind(f"available_pokemon_{pokemon}", "<Button-1>", lambda event, p=pokemon: canvas.on_available_pokemon_click(p))