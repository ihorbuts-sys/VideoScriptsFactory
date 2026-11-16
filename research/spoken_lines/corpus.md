# Spoken lines corpus: short-form food and drink reviewers

Collected 2026-11-11. Every row is a line whose text was seen in a fetched page or a search-result snippet; nothing was
written from memory. Pages were read through a summarising fetch tool told to copy quotes verbatim, so punctuation and
capitalisation may differ slightly from the source; auto-transcripts (SozAI, Rosetta, Atmosfy) keep their own spelling.
Source ids are in `sources.md`; patterns built from these rows are in `patterns.md`.

Evidence level: `transcript` (a transcript page of the video), `quoted` (an article quotes the creator on camera),
`title only` (caption, title or on-screen text, not necessarily spoken), `guidance example` (a template from a guide, not
a creator), `quoted (as mocked)` (a phrase critics quote to mock it). No row is `watched`: no video was watched.
Access is the source's: `opened` (page fetched and read) or `search` (snippet only). Words = whitespace-separated tokens.

Placeholders in brackets ([City], [brand]) are the guide's own. One row (LR4) is an interview, not a video; it is kept for
its score phrasing only. Emoji in two captions (LR14, LR16) were removed.

| Step type | Rows |
|---|---|
| hook/arrive | 34 |
| order | 10 |
| menu | 4 |
| dish reveal | 15 |
| pour/sip | 7 |
| first bite | 27 |
| room | 9 |
| verdict | 80 |
| closing CTA | 14 |
| disclosure | 1 |

## hook/arrive

| # | Line | Words | Creator / format | Ref | Evidence | Access | Where |
|---|---|---|---|---|---|---|---|
| C1 | One bite, everyone knows the rules! | 6 | Dave Portnoy / One Bite | LR1 | quoted | opened | headline + body |
| C2 | For the first time today, I can feel my face a little bit | 13 | Dave Portnoy / One Bite | LR3 | quoted | opened | opening paragraphs |
| C3 | Austin's been talkin' this place up, 'how haven't we gone here?' | 11 | Dave Portnoy / One Bite | LR7 | quoted | opened | body |
| C4 | I got it. Let's try it and rate it one through 10. | 12 | Keith Lee / taste test | LR10 | quoted | opened | body |
| C5 | As always, I don't want any special treatment. I want to be treated like everybody else | 16 | Keith Lee / taste test | LR11 | quoted | opened | Old Lady Gang review |
| C6 | She said she was gonna bug me until she hugged me. Well, she ain't gotta bug me no more. I got it, let's try it and rate it 1-10. | 29 | Keith Lee / taste test | LR13 | quoted | opened | Absolutely Edible Cakes |
| C7 | What's good, everybody? | 3 | Daym Drops (guest) / fast-food review | LR19 | transcript | opened | 03:13 |
| C8 | Which gas station has the cheesiest item? | 7 | Addie Bowley / ranking | LR21 | transcript | opened | 00:00 |
| C9 | You said the portions are huge, so we're going to find out. | 12 | @thedisneygirlie / portion test | LR23 | quoted | opened | opening |
| C10 | Yeh maaate, best place in Landan | 6 | Topjaw | LR30 | quoted | opened | describing the host's opener |
| C11 | I was going to an event in Irvine and was looking for a restaurant to eat dinner at before, and I found all that shabu. | 25 | @ashleyulife, AYCE KBBQ short | LR35 | transcript | opened | segment 1 |
| C12 | Have you been to Junbi Matcha & Tea in Livermore yet? | 11 | @hungere-for-diy, matcha cafe short | LR36 | transcript | opened | segment 1 |
| C13 | They just opened their first Bay Area location a couple weeks ago and you have to give them a visit. | 20 | @hungere-for-diy | LR36 | transcript | opened | segment 2 |
| C14 | Have you been to Boba Studio in Walnut Creek yet? | 10 | @hungere-for-diy, boba short | LR37 | transcript | opened | segment 1 |
| C15 | I think there's a rule out there that you have to have boba every weekend. | 15 | @hungere-for-diy | LR37 | transcript | opened | segment 2 |
| C16 | The dirty, dirty things I would do for Revolution Donuts. | 10 | @food-nd-plants, donut short | LR40 | transcript | opened | segment 2 |
| C17 | So a few months ago, I got this month-long membership to a yoga studio in Bellevue. | 16 | @mahak-masala, matcha short | LR41 | transcript | opened | segment 1 |
| C18 | Boba and tea is my favorite place to get boba drinks. | 11 | @Shaieats, boba short | LR42 | transcript | opened | segment 1 |
| C19 | Today, I wanted to eat a croissant. So I went to a place that sells croissant. And I bought a croissant. | 21 | @nteeats, bakery short | LR43 | transcript | opened | whole transcript |
| C20 | Let's go into Crispy and get us a slice, shall we? | 11 | Adam Richman, Pro Moves (inferred speaker) | LR48 | transcript | opened | before the Krispy visit |
| C21 | It ain't cheap. It's not that easy to get a table. | 11 | Adam Richman, Pro Moves | LR49 | transcript | opened | opening |
| C22 | Is it worth the hype or do just white people like it? | 12 | Amber Richele, SF cafe series | LR52 | quoted | opened | series title |
| C23 | There are over 100 coffee shops in Baltimore, Maryland and I plan to visit every single one. | 17 | Ace Buagas, coffee daily vlog | LR54 | title only (on-screen video text) | opened | intro text |
| C24 | part 9: vault + vine (8/10) | 6 | Gloria Sullivan | LR55 | title only | opened | caption |
| C25 | When I said I would try every coffee shop in D.C., I meant it. | 14 | Domonique Panton (@AsToldByDomm) | LR56 | quoted | opened | tagline at top |
| C26 | Hey everyone, I hope you're having an amazing day. | 9 | Mark Wiens | LR61 | transcript | opened | 0:00 |
| C27 | Make sure everyone is here before you get seated because it is a 2-hour time frame. | 16 | TripNwithUs, AYCE KBBQ/hot pot | LR63 | quoted (page takeaways) | opened | takeaways |
| C28 | We are getting ready to enjoy the all you can eat Korean barbecue and hot pot. | 16 | TripNwithUs | LR63 | quoted (page takeaways) | opened | takeaways |
| C29 | The best-kept secret restaurant in [City] | 6 | hook template (vendor list) | LR73 | guidance example | opened |  |
| C30 | If you live in [City] and have not tried this, you are missing out | 14 | hook template (vendor list) | LR73 | guidance example | opened |  |
| C31 | The [City] food spot with the 4.9-star rating | 8 | hook template (vendor list) | LR73 | guidance example | opened |  |
| C32 | 1-dollar pizza vs 100-dollar pizza. Which is actually better? | 9 | hook template (vendor list) | LR73 | guidance example | opened |  |
| C33 | The dish that has a 2-hour wait every Saturday night | 10 | hook template, venue voice (vendor list) | LR73 | guidance example | opened |  |
| C34 | hidden gem | 2 | mocked phrase | LR74 | quoted (as mocked) | opened |  |

## order

| # | Line | Words | Creator / format | Ref | Evidence | Access | Where |
|---|---|---|---|---|---|---|---|
| C35 | As you can see, I don't have any bag in my hands. | 12 | Keith Lee / taste test | LR11 | quoted | opened | ordering/takeout section |
| C36 | I pay for my food like everybody else. I'm a normal person. I'm a normal customer. | 16 | Keith Lee / taste test | LR11 | quoted | opened | Old Lady Gang review |
| C37 | Let me get two Sweetie meals. | 6 | Daym Drops / drive-thru | LR19 | transcript | opened | 01:10 |
| C38 | We spent a lot of money ordering all the most popular items on the menu. | 15 | Nick DiGiovanni / rating every item | LR20 | transcript | opened | 0:00 |
| C39 | You can place an order at the kiosk. | 8 | @hungere-for-diy | LR37 | transcript | opened | segment 6 |
| C40 | I love their pandan foam, so I got extra for topping. | 11 | @duh_lish | LR39 | transcript | opened | segment 5 |
| C41 | Get the Chinese Mai Tai, not the polished moon. | 9 | @atmosfy "Local Legends" cocktail roundup | LR45 | transcript | opened | segment 2 |
| C42 | This one surprised me. The Beehive on Valencia in the Mission. Order the Espresso Martini. | 15 | @atmosfy | LR45 | transcript | opened | segment 3 |
| C43 | we've ordered slices of lamb beef tendon balls and pork blood | 11 | Mike Chen / First We Feast, curry hot pot | LR47 | transcript | opened | about 9:18 |
| C44 | Medium rare to me is the ultimate pro move here. | 10 | Adam Richman | LR49 | transcript | opened | about 11:32 |

## menu

| # | Line | Words | Creator / format | Ref | Evidence | Access | Where |
|---|---|---|---|---|---|---|---|
| C45 | It's 90 minutes, all you can eat, and there were so many options. | 13 | @ashleyulife | LR35 | transcript | opened | segment 3 |
| C46 | They had a lot of different options, but I like that they also had a variety of topping options as well. | 21 | @hungere-for-diy | LR37 | transcript | opened | segment 7 |
| C47 | Choose from almost the entire menu of drinks to make your own custom flight. | 14 | @duh_lish, boba short | LR39 | transcript | opened | segment 2 |
| C48 | I'll get the menu. | 4 | @maryeatsinthebayarea, matcha cafe short | LR46 | transcript | opened | whole transcript |

## dish reveal

| # | Line | Words | Creator / format | Ref | Evidence | Access | Where |
|---|---|---|---|---|---|---|---|
| C49 | pizza looks pretty good | 4 | Dave Portnoy / One Bite | LR3 | quoted | opened | mid-article |
| C50 | It's huge | 2 | Dave Portnoy / One Bite | LR7 | quoted | opened | opening the box |
| C51 | It's monster...Usually, I think it's a gimmick to go this big | 11 | Dave Portnoy / One Bite | LR7 | quoted | opened | opening the box |
| C52 | That looks....awesome | 2 | Dave Portnoy / One Bite | LR8 | quoted | opened | Pizza Lupo |
| C53 | If we're just looking at this, this looks like it's gonna be knocking on the door of the 8's. | 19 | Dave Portnoy / One Bite | LR8 | quoted | opened | Pizza Lupo |
| C54 | It looks really good, but really bitter. | 7 | Nick DiGiovanni | LR20 | transcript | opened | 0:38 |
| C55 | First of all, why do they give it to you in a bag like this? | 15 | @jes_foodie | LR24 | quoted | opened | body |
| C56 | My favorite was their sea salt caramel banana matcha latte. | 10 | @hungere-for-diy | LR36 | transcript | opened | segment 3 |
| C57 | My creme brulee boba came with a little spoon for the caramelized top. | 13 | @hungere-for-diy | LR37 | transcript | opened | segment 10 |
| C58 | And look at the cheese cream foam on my oolong tea. | 11 | @hungere-for-diy | LR37 | transcript | opened | segment 11 |
| C59 | So all of the components inside the two bowls are edible. | 11 | @lettywong, cocktail bar short | LR44 | transcript | opened | segment 1 |
| C60 | all right look at all this food | 7 | First We Feast, AYCE grill segment | LR47 | transcript | opened | about 2:41 |
| C61 | This is the temple of the t-bone, the palace of the porter house. | 13 | Adam Richman | LR49 | transcript | opened | main-event chapter |
| C62 | It's so shiny and glistening. Not only does it look delicious, but it reminds me of chitlins in the South. | 20 | Calvin on Best Ever Food Review Show | LR51 | quoted | opened | sang cheong section |
| C63 | Oh man, that is a swimming pool of chilies. | 9 | Mark Wiens | LR61 | transcript | opened | 9:09 |

## pour/sip

| # | Line | Words | Creator / format | Ref | Evidence | Access | Where |
|---|---|---|---|---|---|---|---|
| C64 | It's smooth, perfectly balanced, and has the right amount of vanilla to complement the earthy matcha. | 16 | @hungere-for-diy | LR36 | transcript | opened | segment 4 |
| C65 | I love how thick and luscious it was. | 8 | @hungere-for-diy | LR37 | transcript | opened | segment 12 |
| C66 | It honestly just tasted like dessert in a cup. | 9 | @hungere-for-diy, boba short | LR38 | transcript | opened | mid (excerpt) |
| C67 | The Earl Grey is very fruity, but not in a bergamot way | 12 | Gloria Sullivan (@_gloyoyo_), cafe series | LR55 | quoted | opened | Vault + Vine paragraph |
| C68 | smooth / creamy | 3 | Schooner Scorer (Alex Hendy), pint rating | LR57 | quoted (single words) | opened | texture paragraph; 9.2 score; £7.70 in caption |
| C69 | gorgeous | 1 | Food Review Club, Belfast pints | LR64 | quoted (single word) | search | search snippet (Belfast Live via inkl) |
| C70 | absolute creamer | 2 | Prime Mutton (Jason Hackett), Guinness reviews | LR65 | quoted | search | search snippet + headline |

## first bite

| # | Line | Words | Creator / format | Ref | Evidence | Access | Where |
|---|---|---|---|---|---|---|---|
| C71 | Pretty good. | 2 | Dave Portnoy / One Bite | LR2 | quoted | opened | Nico's section |
| C72 | good undercarriage | 2 | Dave Portnoy / One Bite | LR3 | quoted | opened | mid-article |
| C73 | Big time undercarriage | 3 | Dave Portnoy / One Bite | LR8 | quoted | opened | Pizza Lupo |
| C74 | Tangy sauce. Good crust. I like this more than I thought I would coming out of the box. | 18 | Dave Portnoy / One Bite | LR8 | quoted | opened | Ianni's (7.7) |
| C75 | Does this look heavy and eat light? | 7 | Dave Portnoy / One Bite | LR8 | quoted | opened | Iron Born (7.4) |
| C76 | Doughy. That's what jumps out at me | 7 | Dave Portnoy / One Bite | LR8 | quoted | opened | Bella Notte (7.1) |
| C77 | So so good, light, crispy. | 5 | Dave Portnoy / One Bite | LR9 | quoted | opened | Frank's |
| C78 | Good undercarriage… this looks great. | 5 | Dave Portnoy / One Bite | LR33 | quoted | search | search snippet, New Jersey review |
| C79 | I'm going a little bit past good. That's delicious. | 9 | Keith Lee | LR13 | quoted | opened | Terry Black's ribs |
| C80 | more wet and soggy than juicy | 6 | Keith Lee | LR18 | quoted | search | search snippet (5.6 out of 10 tenders) |
| C81 | Oh man, oh man, boo. Oh damn, damn, she's back in the streets with this one, man. | 17 | Daym Drops / fast-food review | LR19 | transcript | opened | 08:06 |
| C82 | The fries aren't soggy. I'm not gonna lie, like, they're not horrible | 12 | @munchinwithmoonshot | LR22 | quoted | opened | fries (5/10) |
| C83 | it's good it's actually it's actually getting better the more I taste it | 13 | Good Mythical Morning | LR29 | transcript | opened | 00:05:47 section |
| C84 | As a matter of fact...while I can maintain my composure it did make my eyes water, a little bit. | 19 | TheReportOfTheWeek (Reviewbrah) | LR31 | quoted | opened | Arby's Diablo Dare |
| C85 | And I'm a sauce girly, and let me tell you, the sauce game was on point. | 16 | @ashleyulife | LR35 | transcript | opened | segment 7 |
| C86 | the seasoning on this was highly addictive and had a perfect crisp | 12 | @hungere-for-diy | LR37 | transcript | opened | segment 17 |
| C87 | that's got a spice yeah it's this each one spice well that's really good | 14 | Mike Chen, hot pot | LR47 | transcript | opened | about 5:25 |
| C88 | Oh my god. Oh my god. | 6 | Adam Richman (inferred speaker) | LR48 | transcript | opened | about 10:00-11:00 |
| C89 | I got to tell you, I don't think I've felt a crust like that before. | 15 | Adam Richman (inferred speaker) | LR48 | transcript | opened | about 10:00 |
| C90 | It's fresh meat cooked perfectly. It's dripping like a bite of steak would. | 13 | Adam Richman | LR49 | transcript | opened | burger chapter |
| C91 | That is a spectacular bite of food. | 7 | Adam Richman | LR49 | transcript | opened | main-event chapter |
| C92 | It's like second dessert. | 4 | Adam Richman | LR49 | transcript | opened | dessert chapter |
| C93 | It's so delicious, it's super salty, super sweet amazing flavours. | 10 | Sonny, Best Ever Food Review Show | LR50 | quoted | opened | ayam kicap section |
| C94 | The whole dish is just a punch to the face. This is the Mike Tyson of cuisine, coming at you with an uppercut. | 23 | Sonny, Best Ever Food Review Show | LR50 | quoted | opened | mee tarik section |
| C95 | The taste is amazing. | 4 | Best Ever Food Review Show | LR51 | quoted | opened | fish stomach section |
| C96 | It's spicy, salty, sweet, and fresh all at once. | 9 | Best Ever Food Review Show (speaker not named) | LR51 | quoted | opened | durian fish curry section |
| C97 | Man, I love tendons | 4 | Mark Wiens, Singapore hawker | LR60 | quoted | opened | $4 beef brisket noodles paragraph |

## room

| # | Line | Words | Creator / format | Ref | Evidence | Access | Where |
|---|---|---|---|---|---|---|---|
| C98 | Great vibes, though | 3 | Dave Portnoy / One Bite | LR5 | quoted | opened | Pleasant Lake Pizza Shark |
| C99 | The customer service was interesting. While the people were nice, the rules they had set were interesting to me. | 19 | Keith Lee | LR11 | quoted | opened | Atlanta Breakfast Club |
| C100 | This is a Golden Corral disguised as a Chinese buffet if I've ever seen one | 15 | Mullet Review / buffet series | LR26 | quoted | opened | body |
| C101 | This is probably one of the worst buffets I've been into, like, in a while | 15 | Mullet Review | LR27 | quoted | opened | Day 2 |
| C102 | The staff all works together, and they are very good about making sure they're staying up on the meats | 19 | @ashleyulife | LR35 | transcript | opened | segment 4 |
| C103 | The cups, merch, and overall aesthetics are so fun. | 9 | @hungere-for-diy | LR36 | transcript | opened | segment 7 |
| C104 | This boba shop was so cute. I love their wall design. | 11 | @hungere-for-diy | LR37 | transcript | opened | segment 4 |
| C105 | Environment: Super welcoming & very cozy. | 6 | Ace Buagas | LR54 | title only (on-screen video text) | opened | OvenBird video |
| C106 | the vibes here definitely outshine the food. | 7 | Tiffy Chen | LR62 | quoted (written) | opened | Olio e Più |

## verdict

| # | Line | Words | Creator / format | Ref | Evidence | Access | Where |
|---|---|---|---|---|---|---|---|
| C107 | I like how it's thin; I like how it's crispy. It's pretty tasty. | 13 | Dave Portnoy / One Bite | LR2 | quoted | opened | Nico's section (score 7.4) |
| C108 | Like, that could have been a low eight, high seven type situation. | 12 | Dave Portnoy (interview, not on camera) | LR4 | quoted | opened | interview quote; phrasing pattern only |
| C109 | Tastes good, eats good, a little greasy | 7 | Dave Portnoy / One Bite | LR5 | quoted | opened | Harwich Port House of Pizza |
| C110 | Hands down, the best pizza I've had on this trip | 10 | Dave Portnoy / One Bite | LR5 | quoted | opened | Stone L'Oven (7.7 real world, 11 Cape Cod scale) |
| C111 | It's almost like this thing can't decide, 'Do I want to be a bar pie or not?' | 17 | Dave Portnoy / One Bite | LR6 | quoted | opened | body |
| C112 | If they made this a personal pie, a bar pie, I would be like 'this is pretty good,' but as a whole pie, I don't know if it is cutting the mustard for me. | 34 | Dave Portnoy / One Bite | LR6 | quoted | opened | closing quotes (avg 6.6) |
| C113 | It's a legit, great pizza | 5 | Dave Portnoy / One Bite | LR8 | quoted | opened | A Slice of New York (8.2) |
| C114 | Shockingly good from the looks of it. | 7 | Dave Portnoy / One Bite | LR8 | quoted | opened | Ianni's |
| C115 | It's a good, good Detroit-style | 5 | Dave Portnoy / One Bite | LR8 | quoted | opened | Iron Born |
| C116 | If you love Detroit, you'll probably go higher. | 8 | Dave Portnoy / One Bite | LR8 | quoted | opened | Iron Born |
| C117 | I can't go 8.1 on a rescore. I'm going 7.9 on this. | 12 | Dave Portnoy / One Bite | LR8 | quoted | opened | Pizzeria Davide |
| C118 | I was gonna give this pizza an 8.1 to begin with, no story involved, I think it's spectacular pizza | 19 | Dave Portnoy / One Bite | LR9 | quoted | opened | Frank's (8.3) |
| C119 | I think this is just style preference, too cheesy for me — 7.4 — but it's still good, I could hammer the whole thing. | 24 | Dave Portnoy / One Bite | LR9 | quoted | opened | Pizza John's |
| C120 | This is a bar pie, a good one | 8 | Dave Portnoy / One Bite | LR9 | quoted | opened | Matthew's |
| C121 | I like the spot, I'd highly recommend it — 7.9 review. | 11 | Dave Portnoy / One Bite | LR9 | quoted | opened | Matthew's |
| C122 | Not bad, it has the Parmesan which I don't always love, I like the vibes. | 15 | Dave Portnoy / One Bite | LR9 | quoted | opened | Johnny Rad's (7.1) |
| C123 | Keyword: My favorite. Before you come in the comments and tell me I'm wrong, I can't be wrong about my opinion. | 21 | Keith Lee / ranking | LR11 | quoted | opened | Chicago chicken ranking |
| C124 | I'm going to be very transparent and honest. I am frustrated | 11 | Keith Lee | LR12 | quoted | opened | body |
| C125 | Overall, with a few minor adjustments, I could see this place being good | 13 | Keith Lee | LR13 | quoted | opened | Thunderbird Pies |
| C126 | Is it the best rib I've ever had? No. Is it good? Absolutely | 13 | Keith Lee | LR13 | quoted | opened | Terry Black's ribs |
| C127 | I 100% see why 17,000 people told me to come here | 11 | Keith Lee | LR13 | quoted | opened | Hutchins BBQ |
| C128 | You can call it peach cobbler, you can call it whatever you want, just call me when you make it | 20 | Keith Lee | LR13 | quoted | opened | Hutchins BBQ peach cobbler |
| C129 | solid 8 | 2 | Keith Lee | LR14 | quoted | opened | Lou's Deli corned beef |
| C130 | Toronto is the top three of places since we've been on this food tour, and it's not even up for debate | 21 | Keith Lee | LR15 | quoted | opened | attributed to TikTok |
| C131 | I could easily see that being a nine and a half or nine. | 13 | Keith Lee | LR15 | quoted | opened | No. 1 Jerk curry goat (7.5 out of 10) |
| C132 | This whole place, I give it 9.8 out of 10 | 10 | Keith Lee | LR17 | quoted | search | search snippet, Breakfast Klub Houston |
| C133 | Mm-hmm, but with these fries today with the Sweetie meal, they she ain't playing, bro. | 15 | Daym Drops / fast-food review | LR19 | transcript | opened | 08:59 |
| C134 | This is an 8.7 out of 10. | 7 | Nick DiGiovanni | LR20 | transcript | opened | 2:47 |
| C135 | This is fantastic. | 3 | Nick DiGiovanni | LR20 | transcript | opened | 2:47 |
| C136 | I might give that a 7.7 out of 10. | 9 | Nick DiGiovanni | LR20 | transcript | opened | 3:36 |
| C137 | Those are fire. | 3 | Addie Bowley | LR21 | transcript | opened | 00:35 |
| C138 | Nine. But don't forget about gold. | 6 | Addie Bowley | LR21 | transcript | opened | 00:47 |
| C139 | It's not bad. It's actually better than I expected it to be | 12 | @munchinwithmoonshot | LR22 | quoted | opened | burger (6.8/10) |
| C140 | I really wanted to hate it. I did. | 8 | @munchinwithmoonshot | LR22 | quoted | opened | headline + body |
| C141 | It tasted good, but it won't be in my top 5 favorites at all. | 14 | @thedisneygirlie | LR23 | quoted | opened | body ($7.50 meal) |
| C142 | Honest rating: like a 3 out of 10. | 8 | @jes_foodie | LR24 | quoted | opened | body ($13 meal) |
| C143 | I feel like I expected a little bit more. | 9 | @jes_foodie | LR24 | quoted | opened | body |
| C144 | Save your money. | 3 | @jessgosolo | LR25 | title only | opened | TikTok caption |
| C145 | This sh**t is goated. This is Golden Corral all day, baby | 11 | Mullet Review | LR26 | quoted | opened | body (censoring is the source's) |
| C146 | Does the Grand Buffet in Knoxville, Tennessee deserve three and a half stars? No, this is a five-star buffet | 19 | Mullet Review | LR26 | quoted | opened | rating |
| C147 | Does the Everything OK buffet deserve 2.9 stars? I'm gonna have to say no. Uh, I think they deserve zero stars. | 21 | Mullet Review | LR27 | quoted | opened | Day 99 |
| C148 | the single burger from Everson Royce bar for eleven dollars it was the best burger in La according to the experts | 21 | Good Mythical Morning | LR29 | transcript | opened | 00:05:47 section |
| C149 | Donuts each cost about three dollars it has 4.5 stars on Yelp making it the People's Choice | 17 | Good Mythical Morning | LR29 | transcript | opened | 00:03:18 section |
| C150 | my disappointment is immeasurable and my day is ruined | 9 | TheReportOfTheWeek (Reviewbrah) | LR32 | title only | opened | KYM sub-entry title / GIF alt text |
| C151 | Fuiyoh! | 1 | Uncle Roger (Nigel Ng) / reaction | LR34 | quoted | search | search snippet, TV Tropes |
| C152 | Haiyaa! | 1 | Uncle Roger (Nigel Ng) / reaction | LR34 | quoted | search | search snippet, TV Tropes |
| C153 | And let me tell you, it was all that. | 9 | @ashleyulife | LR35 | transcript | opened | segment 2 |
| C154 | And for all you can eat, the meat quality was pretty good. | 12 | @ashleyulife | LR35 | transcript | opened | segment 6 |
| C155 | Regardless of what you order, you really can't go wrong here. | 11 | @hungere-for-diy | LR36 | transcript | opened | segment 5 |
| C156 | I would also highly recommend the creamy Americano cloud. | 9 | @hungere-for-diy | LR37 | transcript | opened | segment 13 |
| C157 | I would sell my soul for this company. | 8 | @food-nd-plants | LR40 | transcript | opened | segment 4 |
| C158 | But low-key, I loved it. | 5 | @mahak-masala | LR41 | transcript | opened | segment 5, last |
| C159 | that's the greatest soup ever it's a communal meal have fun have a great conversation | 15 | Mike Chen, hot pot | LR47 | transcript | opened | about 5:25 |
| C160 | The cheese pizza is 40 bucks. The indua goes up to 68. | 12 | Adam Richman, Pro Moves (inferred speaker) | LR48 | transcript | opened | about 8:00 (caption spelling as shown) |
| C161 | In this life, there are many things that are hyped and so few things really live up to them. | 19 | Adam Richman (inferred speaker) | LR48 | transcript | opened | about 11:00 |
| C162 | This is extraordinary. | 3 | Adam Richman (inferred speaker) | LR48 | transcript | opened | about 11:00 |
| C163 | Some things are classic. Remain unchanged, reliable, consistent, and just classy. | 11 | Adam Richman | LR49 | transcript | opened | sign-off |
| C164 | I'm in heaven, man. It doesn't get better than this. | 10 | Sonny, Best Ever Food Review Show | LR50 | quoted | opened | mee tarik section |
| C165 | I think this dish has a bad rep, but if they changed the name from stink beans to something else, it would be amazing. | 24 | Best Ever Food Review Show (Sonny/Calvin) | LR51 | quoted | opened | petai section |
| C166 | I never thought you could take an ingredient people normally throw away and make something so delicious out of it. | 20 | Calvin on Best Ever Food Review Show | LR51 | quoted | opened | sang cheong section |
| C167 | It's a pretty good matcha to me | 7 | Amber Richele, Episode 1 (Motoring Coffee) | LR52 | quoted | opened | Episode 1 paragraph |
| C168 | This is getting a 9.1 from me. This place is very, very solid | 13 | Ryan Keane (@ryaankeane), coffee-shop series | LR53 | quoted | opened | hazelnut iced latte paragraph |
| C169 | Caramel Latte: 8/10, Flavor's strong but balanced, nothing harsh, just a nice finish. | 13 | Ace Buagas | LR54 | title only (on-screen video text) | opened | OvenBird video |
| C170 | It's good. | 2 | Gloria Sullivan | LR55 | quoted | opened | Vault + Vine paragraph |
| C171 | the first 10/10 | 3 | Gloria Sullivan | LR55 | title only | opened | Uncle Bobbie's caption |
| C172 | This was the best pint of Guinness I have ever had. | 11 | Ryan Stephens, pub TikTok | LR58 | quoted | opened | only direct quote |
| C173 | I mean, it was cool, but it wasn't crazy. | 9 | Keith Lee, bakery review | LR59 | quoted | opened | Frozen S'mores (6/10) |
| C174 | If that chocolate was a chocolate bar, it would get a 9/10. | 12 | Keith Lee | LR59 | quoted | opened | Four Leaf Clover |
| C175 | This one brought the score down to a 5.5/10 overall 'cause this is like a 1. | 16 | Keith Lee | LR59 | quoted | opened | fuzzy clovers |
| C176 | That's the first zero I've given out in a long time. | 11 | Keith Lee | LR59 | quoted | opened | cherry basket (0/10) |
| C177 | It's a 10/10 spot to start our day in NYC! | 10 | Tiffy Chen, rating-viral-eats format | LR62 | quoted (written companion post) | opened | Apollo Bagels |
| C178 | I could've easily had a second cup. | 7 | Tiffy Chen | LR62 | quoted (written) | opened | Isshiki Matcha |
| C179 | The portions are huge, and the price is affordable. | 9 | Tiffy Chen | LR62 | quoted (written) | opened | Adel's halal cart ($9 combo) |
| C180 | They're thick, gooey, and worth every bite. | 7 | Tiffy Chen | LR62 | quoted (written) | opened | Levain Bakery |
| C181 | Great experience. Must do. You have to try it. | 9 | TripNwithUs | LR63 | title only (video description) | opened | description |
| C182 | everything you could have asked for | 6 | Food Review Club (Matt), Irish pub pint and stew (9.5/10) | LR64 | quoted | search | search snippet |
| C183 | Selling a croissant for $12 and I was like, this is an insane price. | 14 | @tallbrowngirlll, NYC bakery | LR66 | quoted | search | search snippet |
| C184 | I would say it is worth the price if you share it between friends | 14 | TikToker, Philippe Conticini £25 croissant | LR67 | quoted | search | search snippet |
| C185 | 100% worth it | 3 | mocked phrase | LR74 | quoted (as mocked) | opened |  |
| C186 | life changing | 2 | mocked phrase | LR74 | quoted (as mocked) | opened |  |

## closing CTA

| # | Line | Words | Creator / format | Ref | Evidence | Access | Where |
|---|---|---|---|---|---|---|---|
| C187 | Shoutout Pittsburgh coming in huge with some pizza. | 8 | Dave Portnoy / One Bite | LR8 | quoted | opened | Pizza Lupo |
| C188 | I mean no harm | 4 | Keith Lee | LR11 | quoted | opened | described as recurring sign-off |
| C189 | No malicious intent. | 3 | Keith Lee | LR11 | quoted | opened | described as recurring sign-off |
| C190 | Lous Deli & Detroit Snacks taste test would you try it ? | 12 | Keith Lee | LR14 | title only | opened | TikTok caption (emoji are the source's, not ours) |
| C191 | Frankensons Pizzeria Taste test would you try it ? | 9 | Keith Lee | LR16 | title only | opened | caption, 2023-01-03 |
| C192 | This is a Dame Drops production right here. | 8 | Daym Drops | LR19 | transcript | opened | 13:30 (AI transcript spelling) |
| C193 | If you're in the area, it's worth a visit. | 9 | @ashleyulife | LR35 | transcript | opened | segment 8, last |
| C194 | definitely a spot worth checking out for matcha fans | 9 | @hungere-for-diy | LR36 | transcript | opened | segment 9 |
| C195 | and it was so good I can't wait to go visit again soon | 13 | @hungere-for-diy | LR37 | transcript | opened | segment 19, last |
| C196 | boba pup's labubu series is definitely worth a visit | 9 | @hungere-for-diy | LR38 | transcript | opened | closing (excerpt) |
| C197 | Cheers! | 1 | @duh_lish | LR39 | transcript | opened | segment 7, last |
| C198 | Every spot is on Atmosfy. | 5 | @atmosfy | LR45 | transcript | opened | segment 5, last |
| C199 | all right guys enjoy your meal next time again invite me see ya | 13 | Mike Chen | LR47 | transcript | opened | about 5:25 segment end |
| C200 | run, don't walk | 3 | mocked phrase | LR75 | quoted (as mocked, snippet) | search |  |

## disclosure

| # | Line | Words | Creator / format | Ref | Evidence | Access | Where |
|---|---|---|---|---|---|---|---|
| C201 | Thanks to [brand] for the free product | 7 | regulator wording | LR68 | guidance example | opened |  |
