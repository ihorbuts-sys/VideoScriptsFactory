"""Writes the four v3 kind scripts (dish-review, drink-review, menu-item-review, venue-review) as JSON next to this
file. The JSON files are the source the checker and the catalog build read; this file only keeps the shared steps in
one place. Run: python3 -I author.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

ENTRANCE = ["entrance_sign_tilt_v2", "entrance_walk_in_v2", "entrance_friend_static"]
ROOM = ["room_seated_pan_v2", "room_reveal_plant_v2", "room_static_wide", "room_window_pan_left", "room_bar_pan"]
COUNTER = ["counter_over_shoulder_v2", "counter_edge_to_pass_v2", "menu_board_tilt_up_v2"]
MENU_TABLE = ["menu_card_top_v2", "menu_card_push", "menu_wall_board_item"]
MENU_COUNTER = ["menu_board_tilt_up_v2", "menu_board_truck_v2", "menu_board_static", "counter_over_shoulder_v2"]
PLATED = ["plate_rise_overhead_v2", "plate_high_orbit_v2", "plate_top_orbit", "plate_low_push_in_v2", "plate_turntable"]
CUP = ["steam_top_orbit", "steam_low_backlit_v2", "steam_static_low", "pour_static_45", "pour_side_low_v2"]
GLASS = ["glass_slide_close"]
BITE_FORK = ["bite_pip_dish_v2", "bite_selfie_eye_v2", "bite_friend_three_quarter_v2"]
SIP_CUP = ["sip_cup_only", "sip_selfie_eye_v2", "sip_friend_side_v2", "sip_high_lean_v2"]
HANDOFF_TABLE = ["handoff_plate_lands_v2", "handoff_plate_lands"]
HANDOFF_COUNTER = ["handoff_counter_cup_v2", "counter_hand_receive", "counter_edge_to_pass_v2"]
VERDICT = ["verdict_eye_level_v2", "verdict_friend_eye_v2", "verdict_propped_rear"]
VERDICT_DISH = ["verdict_high_plate_v2", "verdict_plate_after_push"] + VERDICT


def v(line, card, caption, **tags):
    out = {"line": line, "card": card, "caption": caption}
    if tags:
        out["tags"] = tags
    return out


def arrive(subject_word):
    return {
        "key": "arrive", "role": "arrive", "required": True, "title": "Arrive", "camera": "back",
        "where": "Outside, across from the entrance",
        "direction": "Start across from the door with the sign in frame, then walk toward it at an even pace.",
        "guides": ENTRANCE,
        "versions": [
            v("{venue.name}. I came here for " + subject_word + ".", "{venue.name}", "{venue.name}"),
            v("Stopping by {venue.name} for " + subject_word + ".", "At {venue.name}", "{venue.name}"),
            v("First time at {venue.name}.", "First time here", "{venue.name}"),
            v("Starting the day at {venue.name}.", "Morning at {venue.name}", "{venue.name}", daypart="morning"),
            v("Evening stop at {venue.name}.", "Evening at {venue.name}", "{venue.name}", daypart="evening"),
        ],
        "variants": [
            {"when": {"serviceKind": "truck"}, "where": "Across the street from the truck",
             "direction": "Start across the street with the whole truck in frame, then walk toward the window.",
             "guides": ["truck_across_street"]},
        ],
    }


def place():
    return {
        "key": "place", "role": "place", "required": True, "title": "The place", "camera": "back",
        "where": "Inside, from your seat or the doorway",
        "direction": "Hold the phone at chest height and pan slowly across the room from left to right.",
        "guides": ROOM,
        "choice": {"set": "place_word", "preselect": None},
        "versions": [
            v("This is the room at {venue.name}.", "Inside {venue.name}", "{venue.name}"),
            v("Grabbed a table. This is the view from my seat.", "My seat", "{venue.name}"),
            v("Inside {venue.name}. {opinion}", "Inside: {opinion}", "{venue.name}"),
            v("Here is where I am sitting today.", "Today's table", "{venue.name}"),
        ],
        "variants": [
            {"when": {"serviceKind": "counter"}, "title": "The counter", "where": "At the counter, the display in frame",
             "direction": "Stand a step back from the counter and move slowly along the display.",
             "guides": ["counter_display_truck"] + COUNTER,
             "versions": [
                 v("This is the counter at {venue.name}.", "The counter", "{venue.name}"),
                 v("Everything they make is right here.", "The counter", "{venue.name}"),
                 v("The counter at {venue.name}. {opinion}", "Counter: {opinion}", "{venue.name}"),
             ]},
            {"when": {"serviceKind": "truck"}, "title": "The truck", "where": "In front of the truck, the window and the line",
             "direction": "Stand back far enough to fit the window and the people waiting, then move slowly toward the menu.",
             "guides": [], "gap": "truck-place",
             "versions": [
                 v("This is the {venue.name} truck.", "The truck", "{venue.name}"),
                 v("Found the truck. This is the window.", "The window", "{venue.name}"),
                 v("Here is where you order at {venue.name}.", "Order here", "{venue.name}"),
                 v("The truck at {venue.name}. {opinion}", "The truck: {opinion}", "{venue.name}"),
             ]},
        ],
    }


def order(subject_word):
    return {
        "key": "order", "role": "before", "required": False, "title": "Ordering", "camera": "back",
        "where": "At the table, the menu in front of you",
        "direction": "Hold the phone flat above the menu and keep it still on the item you are ordering.",
        "guides": MENU_TABLE,
        "versions": [
            v("Picking from the menu. I'm ordering {menuItem.name}.", "Ordering {menuItem.name}", "The menu"),
            v("Reading the menu. I'm getting {menuItem.name}.", "Getting {menuItem.name}", "What to order"),
            v("Today I'm trying {menuItem.name}.", "Trying {menuItem.name}", "The menu"),
            v("Breakfast menu. I'm going with {menuItem.name}.", "Going with {menuItem.name}", "The menu", menuSection="breakfast"),
        ],
        "variants": [
            {"when": {"serviceKind": "counter"}, "where": "At the counter, the menu board in frame",
             "direction": "Start on the menu board, then tilt down to the counter as you order.", "guides": MENU_COUNTER},
            {"when": {"serviceKind": "truck"}, "where": "At the truck window",
             "direction": "Film the menu on the truck, then the window as you order.", "guides": [], "gap": "truck-order"},
        ],
    }


VERDICT_DIRECTION = "Hold the phone at eye level, look into the lens and answer the question."


def verdict(set_id, question, versions, guides):
    return {
        "key": "verdict", "role": "verdict", "required": True, "title": "Verdict", "camera": "front",
        "where": "At your seat", "direction": VERDICT_DIRECTION, "guides": guides,
        "choice": {"set": set_id, "preselect": None}, "question": question, "versions": versions,
    }


def amenities():
    return {
        "key": "amenities", "role": "amenities", "required": False, "title": "Amenities", "camera": "back",
        "where": "Where the amenity is: the sign, the bowl, the high chair, the lot",
        "direction": "Point the phone at the thing you picked and hold it still for a moment.",
        "guides": ["amenity_point_hold"],
        "choice": {"set": "amenities", "preselect": "business"},
        "versions": [
            v("Also here: {amenity}.", "{amenity}", "{amenity}"),
            v("Good to know at {venue.name}: {amenity}.", "{amenity}", "{amenity}"),
            v("Noticed this here: {amenity}.", "{amenity}", "{amenity}"),
        ],
    }


def food_script(kind, title, entry, kind_chip, main, after, verdict_step, dish_source):
    return {
        "kind": kind, "title": title, "entry": entry, "reviewType": "food", "subjects": kind_chip,
        "dishSource": dish_source,
        "steps": [arrive("{menuItem.name}"), place(), order("{menuItem.name}"), main, after, amenities(), verdict_step],
    }


DISH_MAIN = {
    "key": "main", "role": "main", "required": True, "title": "The dish", "camera": "back", "silent": True,
    "where": "At the table, the plate in front of you",
    "direction": "Follow the guide around the plate; keep the whole dish in frame.",
    "guides": PLATED,
    "versions": [
        v(None, "{menuItem.name}", "{menuItem.name}"),
        v(None, "Here it is: {menuItem.name}", "{menuItem.name}"),
        v(None, "{menuItem.name} at {venue.name}", "{menuItem.name}"),
    ],
    "variants": [
        {"when": {"dishKind": "soups"}, "where": "At the table, the bowl in front of you",
         "direction": "Hold the phone above the bowl and move it slowly so the steam shows.", "guides": ["bowl_steam_overhead"]},
        {"when": {"dishKind": "bowls-sushi"}, "where": "At the table, the bowl or board in front of you",
         "direction": "Hold the phone above the bowl or board and move it slowly around it.", "guides": ["bowl_steam_overhead"]},
        {"when": {"dishKind": "handhelds"}, "where": "Standing or seated, the food in your hand",
         "direction": "Hold it up at eye level and turn it slowly toward the lens.", "guides": [], "gap": "handheld-main"},
    ],
}

DISH_AFTER = {
    "key": "after", "role": "after", "required": False, "title": "First bite", "camera": "back",
    "where": "At the table", "direction": "Lift a forkful toward the lens, then take the bite.",
    "guides": BITE_FORK,
    "choice": {"set": "bite_savory", "preselect": 3},
    "versions": [
        v("First bite of {menuItem.name}. {opinion}", "First bite: {opinion}", "First bite"),
        v("Trying {menuItem.name}. {opinion}", "Verdict so far: {opinion}", "First bite"),
        v("Okay, first bite. {opinion}", "First bite: {opinion}", "First bite"),
    ],
    "variants": [
        {"when": {"dishKind": "soups"}, "title": "First spoonful", "direction": "Lift a spoonful toward the lens, then taste it.",
         "guides": ["spoon_lift_toward_lens"],
         "versions": [
             v("First spoonful of {menuItem.name}. {opinion}", "First spoonful: {opinion}", "First spoonful"),
             v("Trying {menuItem.name}. {opinion}", "First taste: {opinion}", "First spoonful"),
             v("Okay, first spoonful. {opinion}", "First spoonful: {opinion}", "First spoonful"),
         ]},
        {"when": {"dishKind": "handhelds"}, "direction": "Hold it with both hands and take the bite toward the lens.",
         "guides": [], "gap": "hand-after"},
        {"when": {"dishKind": "pizza"}, "direction": "Pick up the pulled slice and take the bite toward the lens.",
         "guides": [], "gap": "hand-after"},
        {"when": {"dishKind": "pastry-bakery"}, "direction": "Break it open toward the lens, then take a bite.",
         "guides": [], "gap": "hand-after", "choice": {"set": "bite_sweet", "preselect": 3}},
        {"when": {"dishKind": "desserts"}, "choice": {"set": "bite_sweet", "preselect": 3},
         "direction": "Take the first spoonful or forkful toward the lens, then taste it."},
        {"when": {"dishKind": "breakfast"}, "choice": {"set": "bite_sweet", "preselect": 3}},
    ],
}

DISH_VERDICT = verdict("verdict_dish", "Would I come back for it?", [
    v("{venue.name}. Would I come back for it? {opinion}", "Would I come back? {opinion}", "{menuItem.name}"),
    v("So, would I come back for {menuItem.name}? {opinion}", "Back for it? {opinion}", "{menuItem.name}"),
    v("Would I come back for it? {opinion}", "Coming back? {opinion}", "{menuItem.name}"),
], VERDICT_DISH)
DISH_VERDICT["variants"] = [
    {"when": {"price": True}, "versions": [
        v("{menuItem.price} at {venue.name}. Would I come back? {opinion}", "Would I come back? {opinion}", "{menuItem.name} · {menuItem.price}"),
        v("{menuItem.name}, {menuItem.price}. Would I come back? {opinion}", "Back for it? {opinion}", "{menuItem.name} · {menuItem.price}"),
        v("It was {menuItem.price}. Would I come back for it? {opinion}", "Coming back? {opinion}", "{menuItem.name} · {menuItem.price}"),
    ]},
]

DRINK_MAIN = {
    "key": "main", "role": "main", "required": True, "title": "The drink", "camera": "back", "silent": True,
    "where": "At the table or the counter, the cup in front of you",
    "direction": "Follow the guide around the cup; keep the whole drink in frame.",
    "guides": CUP,
    "versions": [
        v(None, "{menuItem.name}", "{menuItem.name}"),
        v(None, "Here it is: {menuItem.name}", "{menuItem.name}"),
        v(None, "{menuItem.name} at {venue.name}", "{menuItem.name}"),
    ],
    "variants": [
        {"when": {"drinkKind": "iced-coffee"}, "where": "At the table, the glass in front of you",
         "direction": "Slide the phone slowly toward the glass at table height.", "guides": GLASS},
        {"when": {"drinkKind": "juices-smoothies"}, "where": "At the table, the glass in front of you",
         "direction": "Slide the phone slowly toward the glass at table height.", "guides": GLASS},
        {"when": {"drinkKind": "soft-drinks"}, "where": "At the table, the glass in front of you",
         "direction": "Slide the phone slowly toward the glass at table height.", "guides": GLASS},
        {"when": {"drinkKind": "beer-wine"}, "where": "At the table or the bar, the glass in front of you",
         "direction": "Slide the phone slowly toward the glass at table height.", "guides": GLASS},
        {"when": {"drinkKind": "cocktails"}, "where": "At the table or the bar, the glass in front of you",
         "direction": "Slide the phone slowly toward the glass at table height.", "guides": GLASS},
    ],
}

SIP = lambda name: [
    v("First sip of {menuItem.name}. {opinion}", "First sip: {opinion}", "First sip"),
    v("Trying {menuItem.name}. {opinion}", "First sip: {opinion}", "First sip"),
    v("Okay, first sip. {opinion}", "First sip: {opinion}", "First sip"),
]
DRINK_AFTER = {
    "key": "after", "role": "after", "required": False, "title": "First sip", "camera": "back",
    "where": "At the table", "direction": "Lift the cup toward the lens, then take the sip.",
    "guides": SIP_CUP, "choice": {"set": "sip_coffee", "preselect": 3}, "versions": SIP("coffee"),
    "variants": [
        {"when": {"drinkKind": "tea-matcha"}, "choice": {"set": "sip_tea", "preselect": 3}},
        {"when": {"drinkKind": "iced-coffee"}, "choice": {"set": "sip_iced", "preselect": 3},
         "direction": "Lift the glass toward the lens, then take the sip.", "guides": ["glass_sip_lift"]},
        {"when": {"drinkKind": "juices-smoothies"}, "choice": {"set": "sip_juice", "preselect": 3},
         "direction": "Lift the glass toward the lens, then take the sip.", "guides": ["glass_sip_lift"]},
        {"when": {"drinkKind": "soft-drinks"}, "choice": {"set": "sip_soft", "preselect": 3},
         "direction": "Lift the glass toward the lens, then take the sip.", "guides": ["glass_sip_lift"]},
        {"when": {"drinkKind": "beer-wine"}, "choice": {"set": "sip_beer_wine", "preselect": 3},
         "direction": "Lift the glass toward the lens, then take the sip.", "guides": ["glass_sip_lift"]},
        {"when": {"drinkKind": "cocktails"}, "choice": {"set": "sip_cocktail", "preselect": 3},
         "direction": "Lift the glass toward the lens, then take the sip.", "guides": ["glass_sip_lift"]},
    ],
}

DRINK_VERDICT = verdict("verdict_drink", "Would I order it again?", [
    v("{venue.name}. Would I order it again? {opinion}", "Again? {opinion}", "{menuItem.name}"),
    v("So, would I get {menuItem.name} again? {opinion}", "Ordering again? {opinion}", "{menuItem.name}"),
    v("Would I order it again? {opinion}", "Again? {opinion}", "{menuItem.name}"),
], VERDICT)
DRINK_VERDICT["variants"] = [
    {"when": {"price": True}, "versions": [
        v("{menuItem.price} at {venue.name}. Would I order it again? {opinion}", "Again? {opinion}", "{menuItem.name} · {menuItem.price}"),
        v("{menuItem.name}, {menuItem.price}. Would I get it again? {opinion}", "Ordering again? {opinion}", "{menuItem.name} · {menuItem.price}"),
        v("It was {menuItem.price}. Would I order it again? {opinion}", "Again? {opinion}", "{menuItem.name} · {menuItem.price}"),
    ]},
]

TYPED = lambda hint, chip: {"from": "typed", "maxLength": 40, "hint": hint, "kindChip": chip}

SCRIPTS = {
    "dish-review": food_script("dish-review", "Review a dish", "Food review: Food", "dishKinds", DISH_MAIN, DISH_AFTER, DISH_VERDICT,
                               TYPED("The dish you are reviewing", "dishKinds")),
    "drink-review": food_script("drink-review", "Review a drink", "Food review: Drinks", "drinkKinds", DRINK_MAIN, DRINK_AFTER, DRINK_VERDICT,
                                TYPED("The drink you are reviewing", "drinkKinds")),
}

SCRIPTS["menu-item-review"] = {
    "kind": "menu-item-review", "title": "Review from the menu", "entry": "Food review: From menu", "reviewType": "food",
    "subjects": "fromMenuSection",
    "dishSource": {"from": "menu", "kindFrom": "menuSection",
                   "derive": {"dish": "dish-review", "drink": "drink-review"},
                   "fallback": {"kind": "dish-review", "kindChip": "dishKinds"}},
    "stepsFrom": "derived",
    "note": "The menu item's section sets dish or drink and its kind (tables.json menuSectionMapping); the steps are those of the derived kind, with price set from the item.",
}


def venue_step(key, role, required, title, direction, versions, variants=None, guides=None, choice=None, where="", gap=None):
    s = {"key": key, "role": role, "required": required, "title": title, "camera": "back", "where": where,
         "direction": direction, "guides": guides or [], "versions": versions}
    if not guides:
        s["gap"] = gap or "venue-" + key
    if choice:
        s["choice"] = choice
    if variants:
        s["variants"] = variants
    return s


NO_CLIENTS = "Film the room, the staff who agreed and the tools; keep other visitors out of frame."

VENUE_BEFORE = venue_step("before", "before", False, "Getting started", "Film the order being placed, from the menu to the person taking it.", [
    v("Ordering here works like this.", "How you order", "{venue.name}"),
    v("First, the order.", "Ordering", "{venue.name}"),
    v("This is how you order at {venue.name}.", "How you order", "{venue.name}"),
], variants=[
    {"when": {"subject": "dineIn"}, "title": "Ordering", "where": "At the table", "guides": MENU_TABLE},
    {"when": {"subject": "counter"}, "title": "Ordering", "where": "At the counter", "guides": MENU_COUNTER},
    {"when": {"subject": "truck"}, "title": "Ordering", "where": "At the truck window", "gap": "truck-order"},
    {"when": {"subject": "result"}, "title": "Before", "where": "In the chair, before it starts",
     "direction": "Film the before: a slow pass at eye level, then hold still.", "gap": "result-before",
     "versions": [v("This is the before.", "Before", "Before"), v("Before we start.", "Before", "Before"),
                  v("Here is where we start.", "Before", "Before")]},
    {"when": {"subject": "shopping"}, "title": "Browsing", "where": "Between the shelves",
     "direction": "Walk slowly along one shelf with the phone at chest height.", "gap": "shopping-before",
     "versions": [v("Having a look around {venue.name}.", "Looking around", "{venue.name}"),
                  v("Browsing the shelves first.", "Browsing", "{venue.name}"),
                  v("So much to look at in here.", "Browsing", "{venue.name}")]},
    {"when": {"subject": "experience"}, "title": "Getting ready", "where": "Where you get ready",
     "direction": "Film the gear or the briefing, then yourself ready to go.", "gap": "experience-before",
     "versions": [v("Getting ready.", "Getting ready", "{venue.name}"), v("First, the gear.", "Gearing up", "{venue.name}"),
                  v("Getting set before we start.", "Getting ready", "{venue.name}")]},
    {"when": {"subject": "visit"}, "title": "Meet the team", "where": "At the front desk",
     "direction": NO_CLIENTS + " Ask a staff member who agreed to say hello.", "guides": ["visit_front_desk_hello"],
     "versions": [v("Meeting the team at {venue.name}.", "The team", "{venue.name}"),
                  v("This is the front desk.", "Front desk", "{venue.name}"),
                  v("Saying hello to the team first.", "The team", "{venue.name}")]},
])

VENUE_MAIN = venue_step("main", "main", True, "How it works", "Film the moment you get your order, from their hands to yours.", [
    v("And this is how it arrives.", "Here it comes", "{venue.name}"),
    v("Here it comes.", "Here it comes", "{venue.name}"),
    v("This is how they serve it here.", "Served", "{venue.name}"),
], variants=[
    {"when": {"subject": "dineIn"}, "title": "Served at the table", "where": "At the table", "guides": HANDOFF_TABLE},
    {"when": {"subject": "counter"}, "title": "Pick-up", "where": "At the counter", "guides": HANDOFF_COUNTER},
    {"when": {"subject": "truck"}, "title": "At the window", "where": "At the truck window",
     "direction": "Film the hand-off through the window.", "gap": "truck-handoff"},
    {"when": {"subject": "result"}, "title": "The process", "required": False, "where": "Next to the chair",
     "direction": "Film the hands at work from the side, close and steady.", "gap": "result-main",
     "versions": [v("Here is how it is done.", "The process", "{venue.name}"), v("In the chair now.", "In progress", "{venue.name}"),
                  v("Halfway there.", "In progress", "{venue.name}")]},
    {"when": {"subject": "shopping"}, "title": "The find", "where": "Where you found it",
     "direction": "Hold up what you found, turn it slowly toward the lens.", "gap": "shopping-main",
     "versions": [v("This is what I found.", "The find", "{venue.name}"), v("Found this at {venue.name}.", "The find", "{venue.name}"),
                  v("Look what I found.", "The find", "{venue.name}")]},
    {"when": {"subject": "experience"}, "title": "In action", "where": "In the middle of it",
     "direction": "Film the action wide first, then from your point of view.", "gap": "experience-main",
     "versions": [v("And we are off.", "In action", "{venue.name}"), v("This is it.", "In action", "{venue.name}"),
                  v("Here we go.", "Here we go", "{venue.name}")]},
    {"when": {"subject": "visit"}, "title": "What they do", "where": "In the space they work in",
     "direction": NO_CLIENTS, "guides": ["visit_tools_no_clients"],
     "versions": [v("This is what they do at {venue.name}.", "What they do", "{venue.name}"),
                  v("Here is where they work.", "The space", "{venue.name}"),
                  v("A look at how it works here.", "How it works", "{venue.name}")]},
])

VENUE_AFTER = venue_step("after", "after", False, "The moment after", "Film yourself settling in with what you got.", [
    v("All set.", "All set", "{venue.name}"),
    v("And that is it.", "Done", "{venue.name}"),
    v("Done and settled in.", "All set", "{venue.name}"),
], variants=[
    {"when": {"subject": "dineIn"}, "guides": ["room_tilt_up_from_plate"]},
    {"when": {"subject": "result"}, "title": "The result", "required": True, "where": "In front of the mirror",
     "direction": "Hold still at eye level, then turn slowly to show the result.", "gap": "result-after",
     "versions": [v("And this is the result.", "After", "After"), v("Here is the after.", "After", "After"),
                  v("All done. This is it.", "After", "After")]},
    {"when": {"subject": "shopping"}, "title": "At the checkout", "where": "At the checkout",
     "direction": "Film the bag or the receipt at the counter.", "gap": "shopping-after",
     "versions": [v("Taking this one home.", "Taking it home", "{venue.name}"), v("All bagged up.", "Bagged", "{venue.name}"),
                  v("And that is my haul.", "My haul", "{venue.name}")]},
    {"when": {"subject": "experience"}, "title": "Right after", "where": "Right after it ends",
     "direction": "Turn the phone to yourself and catch your breath on camera.", "guides": ["experience_selfie_after"],
     "versions": [v("Just finished.", "Done", "{venue.name}"), v("That was it.", "Done", "{venue.name}"),
                  v("Catching my breath.", "After", "{venue.name}")]},
    {"when": {"subject": "visit"}, "title": "The takeaway", "where": "On your way out",
     "direction": "Turn the phone to yourself; name what you got from the visit, not a result.", "guides": ["visit_selfie_takeaway"],
     "versions": [v("What I take away from this visit.", "Takeaway", "{venue.name}"),
                  v("Leaving with a plan.", "Takeaway", "{venue.name}"),
                  v("This is what I learned here.", "Takeaway", "{venue.name}")]},
])

VENUE_VERDICT = verdict("verdict_place", "Would I come back here?", [
    v("{venue.name}. Would I come back here? {opinion}", "Coming back? {opinion}", "{venue.name}"),
    v("So, would I come back to {venue.name}? {opinion}", "Back here? {opinion}", "{venue.name}"),
    v("Would I come back? {opinion}", "Coming back? {opinion}", "{venue.name}"),
], VERDICT)
VENUE_VERDICT["variants"] = [
    {"when": {"subject": "result"}, "choice": {"set": "verdict_result", "preselect": None}, "question": "Would I come back for this?"},
    {"when": {"subject": "experience"}, "choice": {"set": "verdict_experience", "preselect": None}, "question": "Would I do it again?",
     "versions": [v("{venue.name}. Would I do it again? {opinion}", "Again? {opinion}", "{venue.name}"),
                  v("So, would I do this again? {opinion}", "Again? {opinion}", "{venue.name}"),
                  v("Would I do it again? {opinion}", "Again? {opinion}", "{venue.name}")]},
    {"when": {"subject": "shopping"}, "choice": {"set": "verdict_shopping", "preselect": None}, "question": "Would I shop here again?",
     "versions": [v("{venue.name}. Would I shop here again? {opinion}", "Back here? {opinion}", "{venue.name}"),
                  v("So, would I shop here again? {opinion}", "Again? {opinion}", "{venue.name}"),
                  v("Would I come back to shop? {opinion}", "Back here? {opinion}", "{venue.name}")]},
    {"when": {"subject": "visit"}, "choice": {"set": "verdict_visit", "preselect": None}, "question": "Would I come back?"},
]

VENUE_PLACE = place()
VENUE_PLACE["variants"] += [
    {"when": {"subject": "result"}, "title": "The salon", "where": "Inside, by the chairs",
     "direction": "Pan slowly across the chairs and mirrors at chest height.", "guides": [], "gap": "result-place",
     "versions": [v("This is {venue.name}.", "Inside {venue.name}", "{venue.name}"), v("Inside {venue.name}. {opinion}", "Inside: {opinion}", "{venue.name}"),
                  v("Here is where it happens.", "Inside", "{venue.name}")]},
    {"when": {"subject": "shopping"}, "title": "The shop", "where": "Inside, by the door",
     "direction": "Pan slowly across the shop at chest height.", "guides": [], "gap": "shopping-place",
     "versions": [v("This is {venue.name}.", "Inside {venue.name}", "{venue.name}"), v("Inside {venue.name}. {opinion}", "Inside: {opinion}", "{venue.name}"),
                  v("Walking into the shop.", "Inside", "{venue.name}")]},
    {"when": {"subject": "experience"}, "title": "The space", "where": "Where it happens",
     "direction": "Film the whole space wide, then hold still.", "guides": [], "gap": "experience-place",
     "versions": [v("This is {venue.name}.", "Inside {venue.name}", "{venue.name}"), v("Inside {venue.name}. {opinion}", "Inside: {opinion}", "{venue.name}"),
                  v("Here is where it happens.", "The space", "{venue.name}")]},
    {"when": {"subject": "visit"}, "title": "The space", "where": "The reception or the room",
     "direction": NO_CLIENTS, "guides": [], "gap": "visit-place",
     "versions": [v("This is {venue.name}.", "Inside {venue.name}", "{venue.name}"), v("Inside {venue.name}. {opinion}", "Inside: {opinion}", "{venue.name}"),
                  v("This is the reception.", "Reception", "{venue.name}")]},
]
VENUE_ARRIVE = arrive("a first look")
VENUE_ARRIVE["versions"] = [
    v("{venue.name}. First time here.", "{venue.name}", "{venue.name}"),
    v("Stopping by {venue.name} today.", "At {venue.name}", "{venue.name}"),
    v("Here is {venue.name}.", "{venue.name}", "{venue.name}"),
    v("Starting the day at {venue.name}.", "Morning at {venue.name}", "{venue.name}", daypart="morning"),
]

# Owner-approved generic venue guides (2026-11-16): the base step serves subjects without a variant of their own.
VENUE_BEFORE["guides"] = ["venue_order_placed"]
VENUE_BEFORE.pop("gap", None)
VENUE_AFTER["guides"] = ["venue_settle_in"]
VENUE_AFTER.pop("gap", None)

SCRIPTS["venue-review"] = {
    "kind": "venue-review", "title": "Review the venue", "entry": "Venue review", "reviewType": "venue",
    "subjects": "venueSubjects",
    "consent": [{"when": {"subject": "visit"}, "required": True,
                 "text": "Only staff who agreed and the space. No patients, clients or children."}],
    "steps": [VENUE_ARRIVE, VENUE_PLACE, VENUE_BEFORE, VENUE_MAIN, VENUE_AFTER, amenities(), VENUE_VERDICT],
}

def own_gap_lists(script):
    """A variant that names a gap shows no guide: give it an explicit empty list so it never inherits the base guides."""
    for step in script.get("steps") or []:
        for var in step.get("variants") or []:
            if "gap" in var and "guides" not in var:
                var["guides"] = []


if __name__ == "__main__":
    for kind, script in SCRIPTS.items():
        own_gap_lists(script)
        with open(os.path.join(HERE, kind + ".json"), "w") as f:
            json.dump(script, f, indent=1, ensure_ascii=False)
            f.write("\n")
        print(kind, len(script.get("steps", [])), "steps")
