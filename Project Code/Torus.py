# https://github.com/marinapapa/a-new-HoPE-model/blob/master/libs/torus.hpp

from Constants import WIDTH, HEIGHT, USE_TOROIDAL_COORD
import pygame as pg


def ofs_coor(a: float, b: float, max: float):
    if USE_TOROIDAL_COORD:
        a0 = b - a
        a1 = a0 + max  # (b + max) - a
        a2 = a0 - max  # (b - max) - a

        if abs(a0) < abs(a1):
            if abs(a0) < abs(a2):
                return a0
            return a2
        if abs(a1) < abs(a2):
            return a1

        return a2
    else:
        return b


def ofs(a: pg.Vector2, b: pg.Vector2):
    if USE_TOROIDAL_COORD:
        return pg.Vector2(ofs_coor(a.x, b.x, WIDTH), ofs_coor(a.y, b.y, HEIGHT))
    return b - a
