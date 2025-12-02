import json

# Load the cleaned file
with open('src/puzzle_bank_clean.json', 'r', encoding='utf-8') as f:
    puzzles = json.load(f)

# Track ALL words globally to avoid any duplicates
global_words = set()

# Better theme-specific replacements (NO NUMBERS!)
theme_replacements = {
    "Blizzards and Storms": ["vortex", "fury", "surge", "howling", "rage", "thunder"],
    "Frozen Water Forms": ["crystals", "slush", "floe", "shard", "sheet", "chunk"],
    "Alpine Skiing": ["carve", "mogul", "alpine", "slope", "peak", "run"],
    "Snowboarding": ["stomp", "bonk", "tweak", "jib", "rail", "land"],
    "Ice Skating Sports": ["twizzle", "spiral", "camel", "death", "biellmann", "layback"],
    "Winter Mountaineering": ["bivvy", "crag", "notch", "rappel", "ascent", "ledge"],
    "Snowmobiling": ["throttle", "carbide", "studs", "track", "runner", "belt"],
    "Cross Country Skiing": ["striding", "herring", "poling", "waxless", "classic", "touring"],
    "Snow Science": ["bonding", "settling", "failure", "profile", "pit", "test"],
    "Avalanche Safety": ["beacon", "alert", "drill", "victim", "rescue", "search"],
    "Winter Camping": ["bivy", "pad", "bag", "tarp", "fuel", "bottle"],
    "Ice Fishing": ["tipup", "jigging", "auger", "shack", "minnow", "hole"],
    "Winter Driving Hazards": ["skid", "spin", "slide", "ditch", "tow", "crash"],
    "Heating Systems": ["burner", "vent", "duct", "valve", "pilot", "furnace"],
    "Winter Fashion": ["parka", "cashmere", "merino", "alpaca", "mohair", "knit"],
    "Winter Soups and Stews": ["hearty", "savory", "ladled", "simmering", "rich", "thick"],
    "Firewood Management": ["maul", "wedge", "rounds", "kindling", "tinder", "logs"],
    "Winter Literature": ["narnia", "chronicles", "fable", "tale", "saga", "story"],
    "Frost Patterns": ["filigree", "lacework", "etching", "tracery", "delicate", "lacy"],
    "Winter Depression Treatment": ["therapy", "counseling", "wellness", "routine", "hygiene", "support"],
    "Polar Exploration": ["depot", "ration", "sledge", "husky", "diary", "tent"],
    "Winter Sports Equipment": ["mount", "tune", "edge", "wax", "base", "tip"],
    "Ice and Snow Formations": ["hummock", "growler", "anchor", "pancake", "brash", "chunk"],
    "Winter Weather Phenomena": ["trough", "jetstream", "isobar", "gradient", "flux", "cell"],
    "Winter Wildlife Behavior": ["molt", "cache", "roost", "browse", "forage", "hunt"],
    "Avalanche and Snow Safety": ["crown", "flank", "runout", "debris", "bed", "path"],
    "Nordic Skiing Techniques": ["skate", "offset", "tuck", "plant", "stride", "poling"],
    "Ice Climbing": ["pick", "torque", "smear", "pillar", "curtain", "screw"],
    "Snow Crystal Types": ["tabular", "skeletal", "aggregate", "habit", "cluster", "branch"],
    "Winter Road Conditions": ["bare", "glazed", "patchy", "plowed", "treated", "slick"],
    "Arctic Geography": ["tundra", "taiga", "fjord", "inlet", "cape", "sound"],
    "Winter Indoor Activities": ["puzzle", "cozy", "craft", "knitting", "baking", "reading"],
    "Snow Play and Yard Fun": ["fort", "angel", "fight", "tunnel", "maze", "pile"],
    "Snow Removal and Home Maintenance": ["scrape", "brush", "pile", "clear", "deice", "salt"],
    "Winter Home Safety": ["alarm", "blanket", "backup", "candle", "drill", "exit"],
    "Winter City Life": ["metro", "rush", "corner", "curb", "taxi", "crowd"],
    "Winter Backyard Birds": ["chickadee", "cardinal", "nuthatch", "finch", "jay", "sparrow"],
    "Sledding and Toboggan Hills": ["tow", "lift", "slope", "speed", "lane", "run"],
    "Winter Markets and Festivals": ["booth", "stall", "lights", "vendor", "stage", "ride"],
    "Cozy Cabin Retreat": ["loft", "beam", "quilt", "hearth", "kettle", "porch"],
    "Winter Health and Illness": ["cough", "fever", "tissue", "vapor", "remedy", "rest"],
    "Subzero Weather Hazards": ["blast", "danger", "alert", "warning", "extreme", "harsh"],
    "Winter Night Sky": ["aurora", "star", "moon", "glow", "arc", "orion"],
    "Evergreen Forest in Winter": ["spruce", "cone", "trunk", "moss", "quiet", "pine"],
    "Ice Sculpture Art": ["chisel", "carve", "shine", "display", "contest", "artist"],
    "Winter Farm Life": ["barn", "hay", "stall", "feed", "cattle", "trough"],
    "Arctic Marine Life": ["whale", "seal", "orca", "dive", "pod", "swim"],
    "Snowshoeing and Winter Hiking": ["trail", "ridge", "summit", "ascent", "route", "trek"],
    "Winter Photography": ["lens", "tripod", "shot", "focus", "exposure", "shutter"],
    "Winter School Day": ["recess", "locker", "bus", "homework", "gym", "lunch"],
    "Ice Age and Glaciation": ["till", "esker", "varve", "kettle", "moraine", "drift"],
}

final_puzzles = []

for puzzle in puzzles:
    theme = puzzle['theme']
    words = puzzle['words']
    
    # Remove words with numbers AND duplicates
    cleaned_words = []
    for w in words:
        w_upper = w.upper()
        # Skip if contains any digit OR already used
        if any(char.isdigit() for char in w):
            continue
        if w_upper not in global_words:
            cleaned_words.append(w)
            global_words.add(w_upper)
    
    # Add unique replacements if needed (also check for numbers!)
    if len(cleaned_words) < 40:
        needed = 40 - len(cleaned_words)
        replacements = theme_replacements.get(theme, [])
        
        for repl in replacements:
            if needed == 0:
                break
            # Skip if contains numbers
            if any(char.isdigit() for char in repl):
                continue
            if repl.upper() not in global_words:
                cleaned_words.append(repl)
                global_words.add(repl.upper())
                needed -= 1
    
    final_puzzles.append({
        "theme": theme,
        "words": cleaned_words[:40]
    })

# Save final version
with open('puzzle_bank_no_duplicates.json', 'w', encoding='utf-8') as f:
    json.dump(final_puzzles, f, indent=2, ensure_ascii=False)

print(f"✅ Fixed! All duplicates removed, NO NUMBERS!")
print(f"Total themes: {len(final_puzzles)}")
print(f"Total unique words: {len(global_words)}")
