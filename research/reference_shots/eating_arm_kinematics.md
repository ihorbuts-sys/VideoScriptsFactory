# Eating with a fork at a table: arm, wrist and head kinematics (2026-11-11)

Why: owner note on bite_friend_three_quarter_v2 (2026-11-11): "elbow is too high on both versions, usually, when human
eat - he keeps his elbow close to body (at the table level) and controls it by moving wrist". Used by
`guides/blender_motion/drafts/people_v2.py` (BITE_POLE, BITE_WRIST_BEND, BITE_LEAN, spec `low_elbow`).

## Sources

| Ref | Source | URL | Status |
|---|---|---|---|
| ER1 | Safaee-Rad R, Shwedyk E, Quanbury AO, Cooper JE. Normal functional range of motion of upper limb joints during performance of three feeding activities (spoon, fork, handled cup). Arch Phys Med Rehabil 1990;71(7):505. 10 able-bodied men, 3D motion capture | https://opact.sdu.edu.tr/vufind/SummonRecord/FETCH-LOGICAL-p181t-af5bcb66f725e5898ffddfb468f905c5799bc73faea1f595ca4da6671ea842452 | search-only (abstract snippet; the page refused the connection) |
| ER2 | Inagaki et al. 2025, seated ADL kinematics incl. eating with chopsticks + plate and spoon + bowl. Front Sports Act Living 10.3389/fspor.2025.1646326. 31 young adults, marker capture 120 Hz, Tables 1-3 | https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2025.1646326/full | opened |
| ER3 | Nakatake J et al. 2021, Exploring whole-body kinematics when eating real foods with the dominant hand in healthy adults. PLoS ONE 16(10):e0259184. 45 adults, inertial sensors, phases reaching / spooning / transport / mouth | https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0259184 | opened (phase tables are images; directional findings and maxima from the text) |
| ER4 | Gentleman's Gazette, How to eat with fork and knife | https://gentlemansgazette.com/eat-fork-knife-etiquette | opened |
| ER5 | Art of Manliness, Guide to dining etiquette | https://www.artofmanliness.com/character/etiquette/guide-dining-etiquette-table-manners/ | opened |
| ER6 | Chan, Online Anthropometry ch. 2-11, sitting elbow height (CityU Hong Kong) | https://personal.cityu.edu.hk/meachan/Online%20Anthropometry/Chapter2/Ch2-11.htm | opened |
| ER7 | Magermans DJ et al. 2005, Requirements for upper extremity motions during activities of daily living. Clin Biomech 20(6):591-9 | https://repository.tudelft.nl/record/uuid:9847426f-51f2-410b-83e9-890418d96dbd | search-only (eating with a spoon is one of the large elbow-flexion tasks; ER2 cites it as needing >= 117 deg) |
| ER8 | University of Kentucky extension, table manners (fcs2101) | https://publications.ca.uky.edu/sites/publications.ca.uky.edu/files/fcs2101.pdf | search-only (snippet: elbows off the table, as close to the body as possible; the PDF text could not be extracted) |
| ER9 | Animation Mentor blog, eating animation reference | https://www.animationmentor.com/?p=95674 | search-only (film yourself; the wrist moves on an arc around the elbow) |
| ER10 | Functional kinematic and kinetic requirements of the upper limb during ADL (prosthetic arm recommendation), arXiv 2408.14361 | https://arxiv.org/html/2408.14361 | opened (eating task: elbow flexion excursion 130 deg, forearm pronation 88 deg, wrist flexion 66 / extension 68 deg peaks across tasks) |

## Numbers

- Shoulder, fork / spoon / cup feeding (ER1): flexion 5-45 deg, abduction 5-35 deg, internal rotation 5-25 deg; elbow
  flexion 70-130 deg; forearm about 40 deg pronation to 60 deg supination (search snippet); wrist rotation negligible.
- Shoulder elevation max / min, mean (SD) (ER2 Table 1): chopsticks 39.2 (10.9) / 20.6 (8.7); spoon 49.7 (11.1) /
  19.9 (7.6); plane of elevation at the peak about 60 deg (between abduction 0 and flexion 90).
- Elbow flexion max / min (ER2 Table 2): chopsticks 122.7 / 48.6; plate 123.4 / 55.7; spoon 121.4 / 48.2; bowl 128.5 /
  53.3. Forearm: supination to -54 (chopsticks) / -49 (spoon). Wrist: extension to -13.7 (chopsticks) / -21.8 (spoon),
  flexion to about 8.
- Trunk flexion max / min (ER2 Table 3): chopsticks 18.8 / 15.7, spoon 19.1 / 15.5 (about 3-4 deg of change); neck
  flexion max 30-34 deg (while looking at the food).
- Phases (ER3): shoulder flexion and abduction and elbow flexion are largest at the mouth; neck flexion is largest while
  loading the spoon and smallest at the mouth; hip (trunk) flexion is largest at the mouth, "to facilitate directing the
  mouth to the food". The table was "at the height of the right elbow", 10 cm from the trunk, seat 40 cm.
- Sitting elbow height above the seat, women 50th percentile (ER6): 23-25 cm (US 23.5). Dining seats sit about 30 cm
  under the table top, so a relaxed elbow lies about at table height.
- Etiquette (ER4, ER5, ER8): forearms close to the body, elbows tucked in; "most of your motions will come from your
  elbow and your wrist"; "the fork moves to your mouth, and your mouth doesn't move to the fork"; sit straight, don't
  hover over the plate.

## What the guide uses (judgement marked)

- Elbow at table height over the plate and close to the ribs; it rises only a few cm at the lips (ER3, ER6, ER4).
  Rig: BITE_POLE (.3, .25, -.9), the elbow down, a little out and back (judgement, tuned to the numbers below).
- Shoulder: abduction up to about 30 deg, flexion under 45 deg, elevation about 25 deg over the plate (ER1, ER2 min 16-21).
  At the lips the elevation is 45 deg, at the top of ER2's chopsticks range (39 +/- 11) (judgement: the 133 mm
  mid-handle grip and the tines-on-the-lips angle the owner approved keep the wrist 28 cm from the shoulder).
- The wrist takes up what the elbow no longer does: the hand turns toward the tines' direction up to 40 deg from the
  forearm (BITE_WRIST_BEND), under the 45 deg limit (judgement; ER2 wrist extension up to 22 deg plus forearm
  supination of about 50 deg, ER1 forearm range).
- Elbow flexion at the lips 104 deg: inside ER1 (70-130), under ER2's mean maximum 121-128 (judgement; same cause as
  the shoulder: the grip and fork angle fix the wrist-to-shoulder distance; not changed because the owner approved
  the grip and the tines-to-lips aim).
- Trunk: 3 deg more forward lean at the lips, head kept upright (BITE_LEAN; ER2 trunk change 3-4 deg, ER3 hip flexion
  largest at the mouth); the fork still travels to the mouth (ER4, ER5). The head itself does not dip (ER3: neck
  flexion smallest at the mouth).
