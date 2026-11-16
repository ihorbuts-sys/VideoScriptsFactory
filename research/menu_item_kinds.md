# Menu item kinds: what venues sell, and how a review of each is filmed

## Sample

Production `businessCollection` on 2026-10-24: 648 venues, 18 with `hasPublishedMenu`. All 18 menus were
fetched with `menusByBusinessId` (the query in `VideoEditorKit/tools/scriptwriter/server.py`); "Demo Business"
was left out as test data, which leaves 17 venues, 1,937 items in 271 non-empty sections. Venues by kind:

| Kind | Venues with a menu |
|---|---|
| dining / food-and-drinks | KPOT Korean BBQ and Hot Pot, El Pinolero Nicaraguan Food, Little Big Burger, Conans Pizza North, La Fruta Feliz, Lucky Robot (sushi), Bombay Express, Sangam Chettinad Indian Cuisine, Kelly's Irish Pub, Que Divino Cocina Mexicana, Kerbey Lane All Day Cafe |
| coffee | KachCafe (Ukrainian-language menu: hot drinks, cold drinks, craft beer, pizza, breakfasts, soups, desserts), Mozart's Coffee Roasters |
| bakery | Angel Donuts and Treats |
| fast-food | Cabo Bob's (and KachCafe's hot dogs) |
| entertainment (craft-beer alias) | Blue Owl Brewing |
| services-health | Workhouse Wellness (in practice a bar and kitchen: 37 local drafts, house cocktails, burgers) |

The sample is thin for coffee (2), bakery (1) and fast food (1), so those review kinds also lean on the dining
menus, which sell the same items (Kerbey Lane's espresso bar, Mozart's pastry case, La Fruta Feliz's tacos).
Food trucks have no published menus at all.

Method: section titles were grouped by keyword into review kinds, then checked by reading item names. Section
titles that are modifiers (milk options, syrups, sauces, add-ons, pizza toppings), kids' menus and retail
shelves (Bombay Express "Retail") were left out: 159 items.

## Review kinds

A review kind is a group of items whose review opens on the same moment and needs the same line. Eleven kinds;
every one of them is covered by a `food-review*` script (last column).

| Review kind | Seen in (venues) | Real items | Opening shot (what to show first) | Line pattern | Script |
|---|---|---|---|---|---|
| Hot drinks: espresso, latte, tea, matcha, chai | 6: Mozart's, KachCafe, Kerbey Lane, Angel Donuts, KPOT, Que Divino | Doppio, Matcha Latte, Masala Chai, Moroccan Mint, Mozart's Breakfast Blend | The pour or the latte art from above, then steam at eye level | name + how it tastes (strength, sweetness, milk) + price + would I order it again | `food-review-drink` |
| Cold drinks: iced coffee, boba, smoothies, juices, aguas frescas, mocktails | 13 (most venues) | Taro Milk Tea, Mango Pineapple Orange Juice, Italian sodas, bubble teas, horchata | The ice and the colour: the shake or stir, condensation, straw going in | name + the flavour that leads + sweet or not + size and price | `food-review-drink` |
| Beer: drafts, flights, cans | 6: Workhouse, Kelly's, KPOT, KachCafe, Kerbey Lane, La Fruta Feliz | Electric Jellyfish, Live Oak Big Bark, Bell's Two Hearted, La Cubetada | The tap pour and the head settling, glass lifted against the light | name and style + local or not + the taste in three words + pint price | `food-review-pour` |
| Cocktails and spirits | 5: Kelly's (85 whiskeys), Workhouse, KPOT, Kerbey Lane, KachCafe | Workhorse Margarita, Bourbon Berry Smash, Pineapple Painkiller, Baby Guinness Shot | The build: the shake, the strain, the garnish going on | name + what is in it + strong or easy + price, happy hour if any | `food-review-pour` |
| Pastries and donuts | 2 (+ bakery kind): Angel Donuts, Mozart's | Raised ring donuts, kolaches, Brioche Cinnamon Roll, Blueberry Lemon Scone, croissants | The break: tearing it in half to show the crumb or the filling | name + texture (flaky, soft, crunchy) + filling + price + how early it sells out | `food-review-sweet` |
| Desserts: cakes, cookies, gelato, macarons | 14 (almost every venue) | Hazelnut Torte, D'Oro Opera, Carrot Cake, macarons, helados, Chocolate Brownie | The cut or the spoon going in: layers, the cross-section | name + the layer or texture + too sweet or not + worth sharing or not | `food-review-sweet` |
| Breakfast and brunch | 9 | Chilaquiles Plate, Migas, Benedicts, pancakes, breakfast tacos, quiche, dosas | Top-down spread, then the yolk break or the syrup pour | name + what is on the plate + the bite that wins + price, served until when | `food-review-table` |
| Handhelds: burgers, tacos, burritos, sandwiches, pizza | 7 + pizza in 2 | Bastrop Burger, Torta Milanesa, Quesabirria, Burrito Feliz, deep pan pizza, The Savage | The cross-section: cutting or pulling it apart, the cheese pull, the two-hand lift | name + what is inside + messy or not + price and whether it fills you up | `food-review-handheld` |
| Plates and bowls: mains, curries, pasta, soups, sushi | 13 + soups in 4 + sushi in 1 | Mole con Tamales, Pescado Frito, Chettinad curries, Caldo de Pollo, Maguro, Nigiri Moriawase | Steam or sauce at a low hero angle, then the fork or chopsticks lift | name + the flavour + portion + price + who it is for | `food-review` |
| Shared tables: hot pot, Korean BBQ, parrilladas, platters, tastings | 3 + tastings at Lucky Robot | KPOT soup bases and meats, Parrilladas, Chef's Tasting menu for 2, Sangam lunch meals | Top-down over the whole table, then the sizzle or the dip at the grill | what we ordered + how it works (all you can eat, cook it yourself) + price per person | `food-review-table` |
| Starters and sides | 12 | Chaats, queso, Fried Pickles, Parmesan Potato Fries, Tajadas, wings | The dip and lift: the crunch or the sauce pull | name + crunch or sauce + order it for the table or not + price | `food-review` |

## What it means for the scripts

- One generic `food-review` cannot open well on all of these: a latte opens on the pour, a burger on the
  cross-section, hot pot on the table from above. The family has six scripts, all `featuresMenuItem: true`:
  `food-review` (plates, bowls, starters; the existing script, kept), `food-review-drink`,
  `food-review-pour`, `food-review-sweet`, `food-review-handheld`, `food-review-table`.
- The kit has no field that ties a menu item to a review kind, so the creator picks the variant by its title
  ("Review a drink"). A host could pick it from the item's section title with the keyword groups above; see
  `HANDOFF.md`.
- Spoken lines use placeholders a creator fills in with the picked item's name and price; the prompter
  reads "the" item in plain words (for example "This is the Bourbon Berry Smash") only when the script writer
  substitutes the item. The bundled text stays generic.
- Prices exist on every item (`variants.amountMinorUnits`), so every review ends on the price.
- Dietary tags are sparse (Angel Donuts' vegan and gluten-free sections are section titles, not tags); scripts do
  not depend on them.
