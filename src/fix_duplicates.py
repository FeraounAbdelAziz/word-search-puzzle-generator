import json

# Load your file
with open('src/8-10.json', 'r', encoding='utf-8') as f:
    puzzles = json.load(f)

# Track ALL words globally to avoid any duplicates
global_words = set()

# Theme-specific replacements for your 40 themes
theme_replacements = {
    "Ocean Creatures": ["plankton", "krill", "reef", "tide", "wave", "current", "brine", "marine", "deep", "surface"],
    "Space & Astronomy": ["void", "space", "astro", "cosmic", "stellar", "lunar", "celestial", "planetary", "void", "expanse"],
    "Farm Animals": ["pasture", "grazing", "feeding", "ranch", "livestock", "herd", "flock", "enclosure", "meadow", "rancher"],
    "Sports & Games": ["athletic", "compete", "field", "court", "arena", "stadium", "league", "season", "playoff", "championship"],
    "Fruits & Vegetables": ["harvest", "organic", "produce", "ripe", "juicy", "nutrition", "vitamin", "fiber", "healthy", "edible"],
    "Weather & Seasons": ["meteorology", "forecast", "pressure", "front", "system", "conditions", "outlook", "pattern", "cycle", "equinox"],
    "Jobs & Careers": ["profession", "occupation", "employment", "career", "job", "work", "labor", "trade", "skill", "expertise"],
    "Musical Instruments": ["melody", "rhythm", "harmony", "note", "chord", "sound", "tone", "pitch", "vibration", "resonance"],
    "Countries & Places": ["nation", "territory", "land", "region", "continent", "capital", "republic", "state", "province", "country"],
    "School Subjects": ["curriculum", "lesson", "course", "class", "lecture", "seminar", "tutorial", "quiz", "test", "exam"],
    "Dinosaurs & Prehistoric": ["ancient", "primordial", "prehistoric", "mesozoic", "paleozoic", "era", "period", "epoch", "remains", "creature"],
    "Holidays & Celebrations": ["festivity", "observance", "commemoration", "anniversary", "jubilee", "gala", "event", "function", "reception", "banquet"],
    "Human Body & Health": ["anatomy", "physiology", "organ", "tissue", "cell", "system", "function", "wellness", "fitness", "vitality"],
    "Transportation & Vehicles": ["transit", "travel", "journey", "voyage", "trip", "commute", "route", "highway", "express", "rapid"],
    "Jungle & Wild Animals": ["predator", "prey", "habitat", "territory", "pack", "pride", "troop", "wilderness", "canine", "feline"],
    "Kitchen & Cooking": ["culinary", "cuisine", "recipe", "dish", "meal", "preparation", "baking", "roasting", "sauteing", "steaming"],
    "Trees & Plants": ["foliage", "vegetation", "flora", "greenery", "canopy", "understory", "forest", "woodland", "grove", "thicket"],
    "Fairy Tales & Fantasy": ["enchantment", "sorcery", "mystical", "mythical", "legendary", "fabled", "magical", "whimsical", "realm", "kingdom"],
    "Colors & Shapes": ["hue", "shade", "tint", "tone", "pigment", "form", "geometry", "polygon", "figure", "angular"],
    "Emotions & Character": ["feelings", "mood", "temperament", "personality", "nature", "disposition", "attitude", "demeanor", "manner", "bearing"],
    "Birds & Flying Creatures": ["avian", "flight", "wingspan", "plumage", "migration", "flock", "roost", "perch", "soar", "glide"],
    "Insects & Bugs": ["insect", "arthropod", "exoskeleton", "antennae", "compound", "metamorphosis", "larvae", "nymph", "instar", "swarm"],
    "Arctic & Polar Animals": ["frigid", "icy", "frosty", "subzero", "freezing", "pack", "floe", "drift", "bergs", "icecap"],
    "Desert Life & Animals": ["arid", "parched", "scorching", "desolate", "wasteland", "scrubland", "badlands", "harsh", "extreme", "barren"],
    "Woodland Forest Animals": ["forest", "woodland", "timberland", "brushland", "thicket", "copse", "glade", "clearing", "underbrush", "canopy"],
    "Art & Crafts Supplies": ["creative", "artistic", "crafting", "handiwork", "project", "design", "pattern", "texture", "medium", "material"],
    "Tools & Building": ["construction", "building", "carpentry", "masonry", "equipment", "apparatus", "device", "implement", "instrument", "tool"],
    "Computer & Technology": ["digital", "electronic", "device", "gadget", "tech", "system", "network", "data", "information", "virtual"],
    "Math & Numbers": ["arithmetic", "mathematics", "calculation", "computation", "numeric", "quantitative", "value", "amount", "total", "figure"],
    "Books & Reading": ["literature", "reading", "publication", "volume", "tome", "manuscript", "text", "prose", "verse", "passage"],
    "Rivers, Lakes & Water": ["aquatic", "waterway", "body", "freshwater", "flowing", "cascade", "torrent", "gushing", "babbling", "meandering"],
    "Gems, Rocks & Minerals": ["precious", "semiprecious", "jewel", "stone", "crystalline", "formation", "deposit", "vein", "seam", "stratum"],
    "Camping & Outdoor Adventures": ["outdoor", "wilderness", "backcountry", "expedition", "excursion", "outing", "jaunt", "ramble", "roam", "wander"],
    "Reptiles & Amphibians": ["herptile", "coldblooded", "ectothermic", "scaly", "slither", "crawl", "bask", "hibernate", "estivate", "burrow"],
    "Mountains & Landforms": ["topography", "elevation", "relief", "contour", "gradient", "incline", "escarpment", "massif", "range", "chain"],
    "Garden & Flowers": ["horticulture", "gardening", "cultivation", "planting", "growing", "tending", "pruning", "weeding", "harvesting", "blooming"],
    "Energy & Power": ["electrical", "mechanical", "kinetic", "potential", "thermal", "radiant", "chemical", "atomic", "sustainable", "renewable"],
    "Clothing & Accessories": ["apparel", "garment", "attire", "outfit", "wardrobe", "fashion", "style", "wear", "clothing", "dress"],
    "Food & Nutrition": ["nourishment", "sustenance", "edible", "consumable", "dietary", "nutritious", "wholesome", "nutritional", "eating", "dining"],
    "Maps & Geography": ["cartography", "topographical", "geographical", "spatial", "location", "position", "coordinates", "bearing", "azimuth", "orientation"],
    "Classroom Objects & Supplies": ["educational", "learning", "studying", "academic", "scholastic", "instructional", "teaching", "lesson", "class", "school"],
    "Action Verbs & Movement": ["motion", "locomotion", "movement", "action", "activity", "gesture", "maneuver", "migrate", "traverse", "navigate"],
    "Time & Calendar Words": ["temporal", "chronological", "duration", "period", "interval", "span", "epoch", "october", "november", "december"],
    "Adjectives & Descriptions": ["descriptive", "quality", "characteristic", "attribute", "trait", "feature", "property", "aspect", "nature", "moderate"],
    "Animal Homes & Habitats": ["dwelling", "shelter", "refuge", "sanctuary", "haven", "retreat", "abode", "residence", "domicile", "biome"],
    "Hospital & Medical": ["medical", "clinical", "healthcare", "wellness", "health", "healing", "remedy", "cure", "treatment", "care"],
    "Restaurant & Dining": ["culinary", "gastronomy", "eatery", "establishment", "dining", "cuisine", "meal", "service", "hospitality", "food"],
    "City & Town Places": ["urban", "metropolitan", "municipal", "civic", "district", "quarter", "zone", "area", "locality", "precinct"],
    "Musical Terms & Sounds": ["musical", "acoustic", "sonic", "auditory", "sound", "audio", "tonal", "melodic", "harmonic", "symphonic"],
    "Opposites & Antonyms": ["opposite", "contrary", "converse", "reverse", "inverse", "between", "middle", "center", "forward", "backward"]
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
with open('8-10_clean.json', 'w', encoding='utf-8') as f:
    json.dump(final_puzzles, f, indent=2, ensure_ascii=False)

print(f"✅ Fixed! All duplicates removed, NO NUMBERS!")
print(f"Total themes: {len(final_puzzles)}")
print(f"Total unique words: {len(global_words)}")
print(f"\nThemes with replacements needed:")
for puzzle in final_puzzles:
    if len(puzzle['words']) < 40:
        print(f"  - {puzzle['theme']}: {len(puzzle['words'])} words")
