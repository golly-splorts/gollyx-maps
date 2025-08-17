import json
import os
import random


def get_vi_pattern_function_map():
    return {
        # Carbomb:
        "detroit_carbomb": detroit_carbomb,
        "jersey_carbomb": jersey_carbomb,
        "northdakota_carbomb": northdakota_carbomb,
        "elko_carbomb": elko_carbomb,

        # Crash:
        "crunchy_crash": crunchy_crash(),
        "spaceship_crash": spaceship_crash(),
        "spaceship_crash2": spaceship_crash2(),
        "big_crash": big_crash(),
        "sea_turtles": sea_turtles(),
        "beach_crash": beach_crash(),
        "mountain_crash": mountain_crash(),
        "flotilla_crash": flotilla_crash(),

        # Party:
        "bunny_party": bunny_party(),
        "domino_party": domino_party(),
        "dove_party": dove_party(),
        "multum_in_party": multum_in_party(),

        # Quad:
        "quad_garden": quad_garden(),
        "quad_barstow": quad_barstow(),
        "quad_bakersfield": quad_bakersfield(),

        # Spacetime complex:
        "spacetime_complex_horizontal": st_h(),
        "spacetime_complex_vertical":   st_v(),

        # Spacetime complex:
        "bifurcating_spacetime_horizontal": st_h(),
        "bifurcating_spacetime_vertical":   st_v(),

        # Standoff:
        "garden_standoff": garden_standoff(),
        "domino_standoff": domino_standoff(),
        "small_standoff": small_standoff(),
        "large_standoff": large_standoff(),
        "garden_standoff2": garden_standoff2(),
        "small_standoff2": small_standoff2(),
        "bisecting_standoff": bisecting_standoff(),
        "oops_all_standoff": oops_all_standoff(),

        # West:
        "west_baltimore": west_baltimore(),,
        "west_boston": west_boston(),,
        "west_seattle": west_seattle(),,
        "west_salt_lake": west_salt_lake(),,
        "west_milwaukee": west_milwaukee(),,
        "west_detroit": west_detroit(),,

        # Wick:
        "wick1": wick1(),
        "wick2": wick2(),

        # Old map patterns:
        "hellmath": hellmath,
        "porchlights": porchlights,
    }


