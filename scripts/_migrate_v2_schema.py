#!/usr/bin/env python3
"""
Migrate pairings-data.json to v2 schema.
Adds drinkType, drinkName, drinkItems[], foodItems[] alongside existing fields.
Old fields (wine, food, store, wineType) kept for backwards compat until HTML is updated.
Run from project root: python scripts/_migrate_v2_schema.py
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

# ── Known winery / drink brands (longest prefix first to avoid partial matches) ──
WINERY_BRANDS = [
    ("Kirkland Signature",          "Kirkland Signature"),
    ("Kirkland",                    "Kirkland Signature"),
    ("Trader Joe's Grand Reserve",  "Trader Joe's"),
    ("Trader Joe's",                "Trader Joe's"),
    ("Sauvignon Republic",          "Sauvignon Republic"),
    ("Famille Perrin",              "Famille Perrin"),
    ("Wölffer Estate",              "Wölffer Estate"),
    ("Wolffer Estate",              "Wölffer Estate"),
    ("Justin",                      "Justin Vineyards & Winery"),
    ("Domaines Brocard",            "Domaines Brocard"),
    ("Joseph Drouhin",              "Joseph Drouhin"),
    ("La Vauvise",                  "La Vauvise"),
    ("Comte de la Chevalière",      "Comte de la Chevalière"),
    ("Comte de la Chevaliere",      "Comte de la Chevalière"),
    ("Ca'Storica",                  "Ca'Storica"),
    ("Espiral",                     "Espiral"),
    ("Mimo Moutinho",               "Mimo Moutinho"),
    ("Super Happy",                 "Super Happy"),
    ("Ruggero di Bardo",            "Ruggero di Bardo"),
    ("Wölffer",                     "Wölffer Estate"),
    ("Pallini",                     "Pallini"),
    ("Aperol",                      "Campari Group"),
    ("Campari",                     "Campari Group"),
    ("La Marca",                    "La Marca"),
    ("Mumm",                        "G.H. Mumm"),
    ("Faff Wine",                   "Faff Wine"),
    ("Valdobbiadene",               "Valdobbiadene"),
    ("Maison Joseph Drouhin",       "Joseph Drouhin"),
    ("Duvergey-Taboureau",          "Duvergey-Taboureau"),
    ("La Crema",                    "La Crema Winery"),
    ("Josh Cellars",                "Josh Cellars"),
    ("Dry Creek Vineyard",          "Dry Creek Vineyard"),
    ("Patroferno",                  "Patroferno"),
    ("La Burgondie",                "La Burgondie"),
    ("Cecilia Beretta",             "Cecilia Beretta"),
    ("Whitehaven",                  "Whitehaven"),
]

# ── Known food / ingredient brands ──
FOOD_BRANDS = [
    ("Trader Joe's",        "Trader Joe's"),
    ("TJ's",                "Trader Joe's"),
    ("Kirkland Signature",  "Kirkland Signature"),
    ("Kirkland",            "Kirkland Signature"),
    ("Kerrygold",           "Kerrygold"),
    ("Ritz",                "Nabisco"),
    ("Kettle Brand",        "Kettle Brand"),
    ("Clancy's",            "Aldi"),
    ("Clancy",              "Aldi"),
    ("La Délice",           "La Délice"),
    ("La Delice",           "La Délice"),
    ("Taco Bell",           "Taco Bell"),
    ("Nacho Supreme",       "Taco Bell"),
    ("Mexican Pizza",       "Taco Bell"),
    ("Cheesy Bean",         "Taco Bell"),
    ("Cool Ranch Doritos",  "Taco Bell"),
    ("Crunch Wrap",         "Taco Bell"),
    ("Caramel Apple Empanada", "Taco Bell"),
    ("Bean Burrito",        "Taco Bell"),
    ("Chicken Bacon Ranch", "Taco Bell"),
]

# ── Wine sub-type inference from name ──
WINE_TYPE_KEYWORDS = {
    "Sparkling": ["prosecco", "champagne", "cava", "crémant", "cremant",
                  "pétillant", "petillant", "sparkling", "moscato d'asti",
                  "vinho verde"],
    "White":     ["sauvignon blanc", "chardonnay", "pinot grigio", "pinot gris",
                  "riesling", "gewürztraminer", "viognier", "albariño", "albarino",
                  "chablis", "sancerre", "gavi", "soave", "grüner veltliner",
                  "gruner veltliner", "blanc", "white", "susumaniello rosato"],
    "Rosé":      ["rosé", "rosato", "summer in a bottle"],
    "Red":       ["merlot", "cabernet", "syrah", "shiraz", "zinfandel", "malbec",
                  "tempranillo", "nebbiolo", "sangiovese", "amarone", "red"],
    "Orange":    ["orange wine", "ramato"],
}

def infer_wine_type(name, existing):
    if existing and existing not in ("Unknown", "N/A", ""):
        return existing
    nl = name.lower()
    for wt, kws in WINE_TYPE_KEYWORDS.items():
        if any(k in nl for k in kws):
            return wt
    return "N/A"

def infer_food_category(s):
    sl = s.lower()
    if any(k in sl for k in ["chip", "crisp", "pretzel", "popcorn", "nut", "almond", "dorito"]):
        return "chips/snack"
    if any(k in sl for k in ["dip", "hummus", "guac", "spread", "salsa", "queso", "caviar"]):
        return "dip/spread"
    if any(k in sl for k in ["cheese", "brie", "cheddar", "gouda", "gorgonzola",
                               "mozzarella", "feta", "parmesan", "gruyère", "leicester",
                               "délice", "delice"]):
        return "cheese"
    if any(k in sl for k in ["prosciutto", "salami", "charcuterie", "meat", "bacon", "ham"]):
        return "charcuterie"
    if any(k in sl for k in ["cracker", "baguette", "bread", "crostini", "ritz"]):
        return "bread/crackers"
    if any(k in sl for k in ["apple", "grape", "berry", "fruit", "peach", "mango", "cherry"]):
        return "fruit"
    if any(k in sl for k in ["chocolate", "candy", "caramel", "sweet", "cookie", "brownie", "empanada"]):
        return "sweet/dessert"
    if any(k in sl for k in ["taco", "burrito", "pizza", "burger", "wrap", "chalupa",
                               "crunch wrap", "mexican", "nacho"]):
        return "meal"
    if any(k in sl for k in ["jelly", "jam", "honey", "butter", "maple", "pepper jelly"]):
        return "condiment"
    if any(k in sl for k in ["jalapeño", "jalapeno", "olive", "pickle", "pepper"]):
        return "pickled/preserved"
    return "other"

def extract_brand(name, brand_table):
    """Match name against brand table. Returns (brand, product, remainder)."""
    for prefix, canonical in brand_table:
        if name.startswith(prefix + " ") or name == prefix:
            product = name[len(prefix):].strip()
            return canonical, product or name
    return None, name

def parse_wine_name(wine_str, existing_wine_type, store):
    """Convert a wine string → list of drinkItem dicts."""
    if not wine_str or wine_str in ("Unknown", ""):
        return [_empty_drink_item()]

    # Strip vintage year prefix "2025 ..."
    vintage = None
    m = re.match(r'^(\d{4})\s+(.+)$', wine_str)
    if m:
        vintage = m.group(1)
        wine_str_clean = m.group(2)
    else:
        wine_str_clean = wine_str

    # Parenthetical component list: "Name (A + B + C)"
    m2 = re.match(r'^(.+?)\s*\((.+)\)$', wine_str_clean)
    if m2:
        components_str = m2.group(2)
        components = [c.strip() for c in re.split(r'\s*\+\s*', components_str)]
        items = []
        for comp in components:
            brand, product = extract_brand(comp, WINERY_BRANDS)
            if brand is None:
                brand, product = extract_brand(comp, FOOD_BRANDS)
            items.append(_drink_item(brand, product, existing_wine_type, store, vintage, comp))
        return items

    brand, product = extract_brand(wine_str_clean, WINERY_BRANDS)
    return [_drink_item(brand, product, existing_wine_type, store, vintage, wine_str_clean)]

def _drink_item(brand, product, existing_wine_type, store, vintage, raw):
    return {
        "brand":       brand,
        "product":     product,
        "productType": _product_type(raw),
        "wineType":    infer_wine_type(raw, existing_wine_type),
        "store":       store if store and store not in ("Unknown", "") else None,
        "region":      None,
        "vintage":     vintage,
        "price":       None,
        "amount":      None,
        "notes":       None,
        "needsReview": brand is None,
    }

def _empty_drink_item():
    return {
        "brand": None, "product": "Unknown", "productType": "wine",
        "wineType": "N/A", "store": None, "region": None, "vintage": None,
        "price": None, "amount": None, "notes": None, "needsReview": True,
    }

def _product_type(name):
    nl = name.lower()
    if any(k in nl for k in ["limoncello", "aperol", "triple sec", "cointreau", "liqueur"]):
        return "liqueur"
    if any(k in nl for k in ["vodka", "gin", "rum", "tequila", "whiskey", "bourbon", "brandy"]):
        return "spirit"
    if any(k in nl for k in ["water", "soda", "juice", "lemonade", "tea", "syrup", "simple syrup"]):
        return "mixer"
    if any(k in nl for k in ["beer", "cider", "lager", "ale"]):
        return "beer"
    return "wine"

def determine_drink_type(category, wine_name):
    nl = (wine_name or "").lower()
    if any(k in nl for k in ["slushie", "slushee", "slushy"]):
        return "Wine Cocktail Recipe"
    if "spritz" in nl:
        return "Spritz Recipe"
    if any(k in nl for k in ["cocktail", "margarita", "mojito", "sangria"]):
        return "Cocktail Recipe"
    if any(k in nl for k in ["mocktail", "non-alcoholic", "non alcoholic"]):
        return "Non-Alcoholic Recipe"
    if category == "recipe":
        return "Wine Cocktail Recipe"
    return "Wine"

def split_food_string(food_str):
    if not food_str or food_str in ("Unknown", ""):
        return []
    # Prefer ' + ' split; fall back to ' / '
    if ' + ' in food_str:
        parts = re.split(r'\s*\+\s*', food_str)
    elif ' / ' in food_str:
        parts = re.split(r'\s*/\s*', food_str)
    else:
        parts = [food_str]
    return [p.strip() for p in parts if p.strip()]

def parse_food_items(food_str, store):
    parts = split_food_string(food_str)
    if not parts:
        return []
    items = []
    for part in parts:
        brand, product = extract_brand(part, FOOD_BRANDS)
        items.append({
            "brand":       brand,
            "product":     product,
            "category":    infer_food_category(part),
            "store":       store if store and store not in ("Unknown", "") else None,
            "price":       None,
            "notes":       None,
            "needsReview": brand is None,
        })
    return items

def migrate_post(p):
    wine      = p.get("wine", "Unknown") or "Unknown"
    food      = p.get("food", "Unknown") or "Unknown"
    store     = p.get("store", "Unknown") or "Unknown"
    wine_type = p.get("wineType", "Unknown") or "Unknown"
    category  = p.get("category", "hidden")

    drink_type  = determine_drink_type(category, wine)
    drink_items = parse_wine_name(wine, wine_type, store)
    food_items  = parse_food_items(food, store)

    new = dict(p)   # keep ALL existing fields untouched
    new["drinkType"]  = drink_type
    new["drinkName"]  = wine       # replaces "wine" for display — old "wine" field kept for compat
    new["drinkItems"] = drink_items
    new["foodItems"]  = food_items
    return new


# ── Run ──
with open("pairings-data.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

migrated = [migrate_post(p) for p in data]

# ── Report ──
visible = [p for p in migrated if p.get("category") != "hidden"]
drink_nr = [(p["drinkName"], i["product"]) for p in visible for i in p["drinkItems"] if i.get("needsReview")]
food_nr  = [(p["drinkName"], i["product"]) for p in visible for i in p["foodItems"]  if i.get("needsReview")]

print(f"Migrated {len(migrated)} posts ({len(visible)} visible, {len(migrated)-len(visible)} hidden)")
print(f"Drink items needing brand review : {len(drink_nr)}")
print(f"Food items needing brand review  : {len(food_nr)}")

if drink_nr:
    print("\n── DRINK BRAND UNKNOWN ──")
    for wine_name, product in drink_nr:
        print(f"  [{wine_name}] → {product!r}")

if food_nr:
    print("\n── FOOD BRAND UNKNOWN (first 30) ──")
    for wine_name, product in food_nr[:30]:
        print(f"  [{wine_name}] → {product!r}")

# Show drinkType breakdown
from collections import Counter
dt_counts = Counter(p["drinkType"] for p in visible)
print("\n── drinkType breakdown ──")
for dt, n in sorted(dt_counts.items()):
    print(f"  {dt}: {n}")

# Write
with open("pairings-data.json", "w", encoding="utf-8") as f:
    json.dump(migrated, f, indent=2, ensure_ascii=False)

print("\nDone. Wrote pairings-data.json")
