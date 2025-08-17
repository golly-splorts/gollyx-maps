import json
import os
import random
from .geom import hflip_pattern, vflip_pattern
from .utils import pattern2url
from .patterns import get_grid_empty, pattern_union, get_pattern, get_grid_pattern
from .utils import pattern2url, retry_on_failure

from .hellmouth import (
    eightpi_twocolor,
    eightr_twocolor,
    fourrabbits_twocolor,
    quadjustyna_twocolor,
    random_twocolor,
    randompartition_twocolor,
    spaceshipcluster_twocolor,
    spaceshipcrash_twocolor,
    timebomb_oscillators_twocolor,
    timebomb_randomoscillators_twocolor,
    twoacorn_twocolor,
    twomultum_twocolor,
    twospaceshipgenerators_twocolor,
    bigsegment_twocolor,
    randomsegment_twocolor,
    spaceshipsegment_twocolor,
    randommethuselahs_twocolor,
    switchengines_twocolor,
    orchard_twocolor,
    rabbitfarm_twocolor,
    spiders_twocolor,
    crabs_twocolor,
)
from .toroidal import (
    donutmath_twocolor,
    donuttimebomb_twocolor,
    donuttimebombredux_twocolor,
    doublegaussian_twocolor,
    porchlights_twocolor,
)


def get_klein_pattern_function_map():
    return {
        # Toroidal
        "kleinmath": donutmath_twocolor,
        "kleintimebomb": donuttimebomb_twocolor,
        "kleintimebombredux": donuttimebombredux_twocolor,
        "doublegaussian": doublegaussian_twocolor,
        "porchlights": porchlights_twocolor,
        # Hellmouth
        "classictimebomb": timebomb_oscillators_twocolor,
        "eightpi": eightpi_twocolor,
        "eightr": eightr_twocolor,
        "fourrabbits": fourrabbits_twocolor,
        "quadjustyna": quadjustyna_twocolor,
        "random": random_twocolor,
        "randompartition": randompartition_twocolor,
        "spaceshipcluster": spaceshipcluster_twocolor,
        "spaceshipcrash": spaceshipcrash_twocolor,
        "twoacorn": twoacorn_twocolor,
        "twomultum": twomultum_twocolor,
        "twospaceshipgenerators": twospaceshipgenerators_twocolor,
        "bigsegment": bigsegment_twocolor,
        "randomsegment": randomsegment_twocolor,
        "spaceshipsegment": spaceshipsegment_twocolor,
        "randommethuselahs": randommethuselahs_twocolor,
        "switchengines": switchengines_twocolor,
        "orchard": orchard_twocolor,
        "rabbitfarm": rabbitfarm_twocolor,
        "spiders": spiders_twocolor,
        "crabs": crabs_twocolor,
    }

