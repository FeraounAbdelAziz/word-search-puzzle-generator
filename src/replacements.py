# src/replacements.py

# All keys are UPPERCASE because your analyzer output is uppercased.
# Theme names must match exactly what you use in the JSON.

REPLACEMENTS = {
    # ----- POWDER (×5) -----
    "POWDER": {
        "Frozen Water Forms": "powdersnow",
        "Snowboarding": "powstash",
        "Snowmobiling": "powderturns",
        "Snow Science": "lowdensitysnow",
        # Alpine Skiing is the "owner" and keeps "powder"
    },

    # ----- WHITEOUT (×4) -----
    "WHITEOUT": {
        "Winter Mountaineering": "mountainwhiteout",
        "Polar Exploration": "polarwhiteout",
        "Winter Driving Hazards": "blindingconditions",
        # Blizzards and Storms owns "whiteout"
    },

    # ----- CORNICE (×5) -----
    "CORNICE": {
        "Ice and Snow Formations": "snowcornice",
        "Avalanche and Snow Safety": "cornicefall",
        "Snow Science": "cornicelip",
        "Blizzards and Storms": "snowoverhang",
        # Winter Mountaineering owns "cornice"
    },

    # ----- BOOTS (×5) -----
    "BOOTS": {
        "Snowmobiling": "snowmobileboots",
        "Winter Camping": "campboots",
        "Winter Fashion": "winterboots",
        "Cross Country Skiing": "skateboots",
        # Winter Sports Equipment (or Alpine Skiing) owns "boots"
    },

    # ----- INSULATION (×5) -----
    "INSULATION": {
        "Winter Fashion": "thermalinsulation",
        "Winter Camping": "sleepingpadinsulation",
        "Firewood Management": "heatretention",
        "Snow Science": "insulatinglayer",
        # Heating Systems owns "insulation"
    },

    # ----- BACKCOUNTRY (×4) -----
    "BACKCOUNTRY": {
        "Snowmobiling": "backcountryriding",
        "Cross Country Skiing": "backcountrytouring",
        "Snowboarding": "backcountrylines",
        # Alpine Skiing owns "backcountry"
    },

    # ----- BINDINGS (×4) -----
    "BINDINGS": {
        "Snowboarding": "strapbindings",
        "Winter Sports Equipment": "mountbindings",
        "Cross Country Skiing": "nordicbindings",
        # Alpine Skiing owns "bindings"
    },

    # ----- CREVASSE (×4) -----
    "CREVASSE": {
        "Ice and Snow Formations": "crevassefield",
        "Snow Science": "crevasseweakness",
        "Polar Exploration": "crevassezone",
        # Winter Mountaineering owns "crevasse"
    },

    # ----- GRAUPEL (×4) -----
    "GRAUPEL": {
        "Ice and Snow Formations": "graupelshowers",
        "Winter Weather Phenomena": "graupelstorm",
        "Snow Crystal Types": "graupelparticles",
        # Snow Science owns "graupel"
    },

    # ----- ICE (×4) -----
    "ICE": {
        "Frozen Water Forms": "solidice",
        "Ice Climbing": "waterfallice",
        "Polar Exploration": "packicefield",
        # Ice Fishing or Ice and Snow Formations can own plain "ice"
    },

    # ----- RHYTHM (×4) -----
    "RHYTHM": {
        "Alpine Skiing": "turnrhythm",
        "Snowboarding": "flowrhythm",
        "Winter Depression Treatment": "sleeprhythm",
        # Nordic Skiing Techniques or Cross Country Skiing owns "rhythm"
    },

    # ----- ADVISORY (×3) -----
    "ADVISORY": {
        "Avalanche Safety": "avalancheadvisory",
        "Winter Road Conditions": "traveladvisory",
        # Blizzards and Storms owns "advisory"
    },

    # ----- BEACON (×2) -----
    "BEACON": {
        "Snowmobiling": "sledbeacon",
        # Avalanche Safety owns "beacon"
    },

    # ----- SHOVEL (×3) -----
    "SHOVEL": {
        "Winter Camping": "campshovel",
        "Snowmobiling": "sledshovel",
        # Avalanche Safety or Firewood Management owns "shovel"
    },

    # ----- PROBE (×2) -----
    "PROBE": {
        "Snowmobiling": "sledprobe",
        # Avalanche Safety owns "probe"
    },

    # ----- SLED (×3) -----
    "SLED": {
        "Winter Camping": "pulksled",
        "Firewood Management": "logsled",
        # Snowmobiling or Ice Fishing owns "sled"
    },

    # ----- SNOWPACK (×3) -----
    "SNOWPACK": {
        "Avalanche and Snow Safety": "snowslab",
        "Polar Exploration": "polarpack",
        # Snow Science owns "snowpack"
    },

    # ----- RIDGE (×3) -----
    "RIDGE": {
        "Ice and Snow Formations": "pressureridge",
        "Blizzards and Storms": "snowridge",
        # Winter Mountaineering owns "ridge"
    },

    # ----- GLOVES (×3) -----
    "GLOVES": {
        "Snowmobiling": "heatedgloves",
        "Winter Camping": "campgloves",
        # Winter Fashion or Winter Sports Equipment owns "gloves"
    },

    # ----- HELMET (×3) -----
    "HELMET": {
        "Snowmobiling": "fullfacehelmet",
        "Winter Mountaineering": "climbinghelmet",
        # Alpine Skiing / Snowboarding / Equipment owns "helmet"
    },

    # ----- GOGGLES (×2) -----
    "GOGGLES": {
        "Snowmobiling": "sledgoggles",
        # Alpine / Snowboard / Equipment owns "goggles"
    },

    # ----- TRAIL (×3) -----
    "TRAIL": {
        "Cross Country Skiing": "skitrail",
        "Winter Wildlife": "animaltrail",
        # Snowmobiling owns "trail"
    },

    # ----- TRACTION (×2) -----
    "TRACTION": {
        "Winter Road Conditions": "tiretraction",
        # Winter Driving Hazards owns "traction"
    },

    # ----- BLACKICE (×2) -----
    "BLACKICE": {
        "Winter Road Conditions": "roadblackice",
        # Winter Driving Hazards owns "blackice"
    },

    # ----- SKIS (×3) -----
    "SKIS": {
        "Winter Sports Equipment": "skiquiver",
        "Cross Country Skiing": "nordicskis",
        # Alpine Skiing owns "skis"
    },

    # You can keep extending this dict for the rest of the 164 duplicates.
}
