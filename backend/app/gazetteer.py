"""Kyiv Spatial Gazetteer and Toponymic Database.

Contains definitions of Kyiv administrative districts, microdistricts,
suburban approach corridors, and outer transit locations.
"""
from typing import Dict, List, Any, Optional

# Kyiv Center coordinates
KYIV_CENTER = (50.4501, 30.5234)

# 10 Kyiv Administrative Districts with centroids and bounding polygons
KYIV_DISTRICTS: Dict[str, Dict[str, Any]] = {
    "Obolonskyi": {
        "ukr_name": "Оболонський",
        "aliases": ["оболонь", "оболонський", "мінський масив", "пріорка", "пуща-водиця"],
        "center": (50.505, 30.498),
        # Simplified representative polygon [lat, lon]
        "polygon": [
            [50.480, 30.450],
            [50.550, 30.450],
            [50.550, 30.535],
            [50.510, 30.530],
            [50.480, 30.490],
            [50.480, 30.450]
        ]
    },
    "Podilskyi": {
        "ukr_name": "Подільський",
        "aliases": ["поділ", "подільський", "куренівка", "виноградар", "вітряні гори"],
        "center": (50.472, 30.468),
        "polygon": [
            [50.450, 30.420],
            [50.510, 30.380],
            [50.515, 30.450],
            [50.480, 30.510],
            [50.455, 30.515],
            [50.450, 30.420]
        ]
    },
    "Shevchenkivskyi": {
        "ukr_name": "Шевченківський",
        "aliases": ["шевченківський", "лук'янівка", "луцьянівка", "сирець", "нивки", "татарка"],
        "center": (50.458, 30.465),
        "polygon": [
            [50.435, 30.420],
            [50.480, 30.420],
            [50.480, 30.495],
            [50.445, 30.515],
            [50.435, 30.420]
        ]
    },
    "Pecherskyi": {
        "ukr_name": "Печерський",
        "aliases": ["печерськ", "печерський", "липки", "звіринець"],
        "center": (50.428, 30.548),
        "polygon": [
            [50.405, 30.525],
            [50.448, 30.520],
            [50.448, 30.565],
            [50.410, 30.575],
            [50.405, 30.525]
        ]
    },
    "Holosiivskyi": {
        "ukr_name": "Голосіївський",
        "aliases": ["голосієво", "голосіївський", "теремки", "деміївка", "деміївки", "корчувате", "пирогів", "китаїв"],
        "center": (50.380, 30.515),
        "polygon": [
            [50.320, 30.470],
            [50.410, 30.490],
            [50.410, 30.560],
            [50.330, 30.570],
            [50.320, 30.470]
        ]
    },
    "Solomianskyi": {
        "ukr_name": "Солом'янський",
        "aliases": ["солом'янка", "солом'янський", "соломка", "відрадний", "жуляни", "караваєві дачі", "чоколівка"],
        "center": (50.425, 30.445),
        "polygon": [
            [50.395, 30.390],
            [50.450, 30.410],
            [50.450, 30.480],
            [50.400, 30.480],
            [50.395, 30.390]
        ]
    },
    "Sviatoshynskyi": {
        "ukr_name": "Святошинський",
        "aliases": ["святошин", "святошинський", "борщагівка", "академмістечко", "біличі", "новобіличі"],
        "center": (50.455, 30.365),
        "polygon": [
            [50.415, 30.300],
            [50.490, 30.300],
            [50.490, 30.400],
            [50.415, 30.400],
            [50.415, 30.300]
        ]
    },
    "Desnianskyi": {
        "ukr_name": "Деснянський",
        "aliases": ["деснянський", "троєщина", "лісовий", "биківня"],
        "center": (50.515, 30.605),
        "polygon": [
            [50.480, 30.550],
            [50.565, 30.550],
            [50.565, 30.680],
            [50.480, 30.660],
            [50.480, 30.550]
        ]
    },
    "Dniprovskyi": {
        "ukr_name": "Дніпровський",
        "aliases": ["дніпровський", "русанівка", "воскресенка", "березняки", "радужний", "лівобережна"],
        "center": (50.455, 30.600),
        "polygon": [
            [50.425, 30.550],
            [50.485, 30.550],
            [50.485, 30.640],
            [50.425, 30.630],
            [50.425, 30.550]
        ]
    },
    "Darnytskyi": {
        "ukr_name": "Дарницький",
        "aliases": ["дарницький", "дарниця", "позняки", "осокорки", "харківський масив", "бортничі", "червоний хутір"],
        "center": (50.398, 30.635),
        "polygon": [
            [50.350, 30.590],
            [50.435, 30.590],
            [50.435, 30.720],
            [50.350, 30.720],
            [50.350, 30.590]
        ]
    }
}

# Suburb corridors leading into Kyiv
KYIV_SUBURBS: Dict[str, Dict[str, Any]] = {
    "vyshhorod": {
        "ukr_name": "Вишгород",
        "aliases": ["вишгород", "вишгородський", "вишгорода", "вишгородського"],
        "primary_districts": ["Obolonskyi"],
        "entry_point": (50.584, 30.489),
        "bearing_deg": 180.0
    },
    "khotianivka": {
        "ukr_name": "Хотянівка",
        "aliases": ["хотянівка", "хотянівки"],
        "primary_districts": ["Obolonskyi", "Desnianskyi"],
        "entry_point": (50.605, 30.560),
        "bearing_deg": 195.0
    },
    "brovary": {
        "ukr_name": "Бровари",
        "aliases": ["бровари", "броварів", "броварський", "броварського"],
        "primary_districts": ["Darnytskyi", "Desnianskyi", "Dniprovskyi"],
        "entry_point": (50.512, 30.792),
        "bearing_deg": 250.0
    },
    "boryspil": {
        "ukr_name": "Бориспіль",
        "aliases": ["бориспіль", "борисполя", "бориспільський", "бориспільського"],
        "primary_districts": ["Darnytskyi"],
        "entry_point": (50.345, 30.955),
        "bearing_deg": 295.0
    },
    "vasylkiv": {
        "ukr_name": "Васильків",
        "aliases": ["васильків", "василькова", "васильківський", "васильківського"],
        "primary_districts": ["Holosiivskyi", "Solomianskyi"],
        "entry_point": (50.178, 30.315),
        "bearing_deg": 30.0
    },
    "obukhiv": {
        "ukr_name": "Обухів",
        "aliases": ["обухів", "обухова", "обухівський", "обухівського", "козин", "козина"],
        "primary_districts": ["Holosiivskyi"],
        "entry_point": (50.127, 30.635),
        "bearing_deg": 350.0
    },
    "irpin": {
        "ukr_name": "Ірпінь",
        "aliases": ["ірпінь", "ірпеня", "ірпінський", "буча", "бучі", "гостомель", "гостомеля"],
        "primary_districts": ["Sviatoshynskyi", "Podilskyi"],
        "entry_point": (50.520, 30.245),
        "bearing_deg": 125.0
    },
    "hlevakha": {
        "ukr_name": "Глеваха",
        "aliases": ["глеваха", "глевахи"],
        "primary_districts": ["Solomianskyi", "Holosiivskyi"],
        "entry_point": (50.266, 30.315),
        "bearing_deg": 35.0
    }
}

# Outside transit regions (away from Kyiv municipal borders)
TRANSIT_LOCATIONS: List[str] = [
    "біла церква", "білої церкви", "білій церкві",
    "фастів", "фастова", "фастові",
    "переяслав", "яготин", "миронівка", "богуслав", "сквира", "тетіїв",
    "житомирщин", "черкащин", "вінниччин", "полтавщин", "чернігівщин"
]
