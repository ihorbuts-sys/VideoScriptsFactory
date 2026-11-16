"""Regression set for line_lint.py: the handoff's "Don't" examples (the script review findings, 2026-11-13) must each
break their rule, its "Do" examples must pass. Run: python3 -I scripts/tools/test_line_lint.py"""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import line_lint  # noqa: E402
import step_fields  # noqa: E402

SETS = {s["id"]: s for s in step_fields.OPINION_SETS}
TEMPLATE = {"id": "first-visit", "featuresMenuItem": True, "steps": []}
BASE = {"id": "verdict", "complexity": "easy", "seconds": 8, "titleFacts": ["{venue.name}"], "card": "The verdict",
        "guides": [], "direction": "Front camera at arm's length."}


def rules(**step):
    s = dict(copy.deepcopy(BASE), **step)
    t = dict(TEMPLATE, steps=[s])
    return {r for r, _, _ in line_lint.step_rules(t, s, SETS, True)}


class DontExamples(unittest.TestCase):
    def test_hearsay(self):
        for line in ("The barista says it's their best.", "Found the place everyone keeps telling me about.",
                     "Asked what I should get, and they all said this one."):
            self.assertIn("L1", rules(line=line), line)

    def test_judgement_outside_slot(self):
        for line in ("Certainly.", "Smooth, not bitter, and the milk is silky.", "Okay, wow.",
                     "Better. I am finishing all of this."):
            self.assertIn("L3", rules(line=line), line)

    def test_teaser(self):
        for line in ("Okay, first sip. Here's how it tastes.", "That's {venue.name}. Here's why I'd come back.",
                     "Would I come back for this? Here is my honest answer."):
            self.assertIn("L2", rules(line=line), line)

    def test_caption_facts_only(self):
        for caption in ("Worth the price", "Not what I expected", "Go try it", "Worth the hype?"):
            self.assertIn("L4", rules(line="Here is the cup.", caption=caption), caption)

    def test_time_of_day(self):
        for line in ("Look at this room. This is the mood for tonight.", "New spot on my walk to work."):
            self.assertIn("L5", rules(line=line), line)

    def test_data_the_script_lacks(self):
        self.assertIn("L6", rules(line="Here is the cup.", direction="Say the price, the street, and why."))

    def test_complex_step_is_silent(self):
        self.assertIn("L7", rules(complexity="complex", line="Look at this plate."))

    def test_fits_the_step(self):
        self.assertIn("L8", rules(seconds=4, line="First time at {venue.name}, and I want to see the whole room now."))

    def test_price_needs_no_price_variant(self):
        self.assertIn("L10", rules(line="{menuItem.price} at {venue.name}.", caption="{menuItem.price}"))

    def test_slot_needs_block(self):
        self.assertIn("L11", rules(line="Would I come back? {opinion}"))

    def test_verdict_never_preselected(self):
        found = rules(line="Would I come back? {opinion}",
                      opinion={"set": "verdict_answer", "preselect": "certainly", "order": ["certainly"]})
        self.assertIn("L11", found)

    def test_banned_claims(self):
        for line in ("Best in town.", "Their famous {menuItem.name}."):
            self.assertIn("L12", rules(line=line), line)

    def test_card(self):
        self.assertIn("L14", rules(line="Here is the cup.", card=None, titleFacts=None))
        self.assertIn("L14", rules(line="Here is the cup.", card="This card has far too many words in it"))


class ShortNames(unittest.TestCase):
    def test_no_short_name_slots(self):
        self.assertIn("L6", rules(line="Back at {venue.shortName} for the {menuItem.name}."))

    def test_long_caption_wraps_as_warning(self):
        self.assertIn("L9-caption", rules(line="Picking from the menu.", caption="Ordered: {menuItem.name}"))


class DoExamples(unittest.TestCase):
    def test_handoff_frames_pass(self):
        # The handoff's frames, shortened 2026-11-13 so long real names still fit 8 s (no short names exist).
        ok = dict(line="{menuItem.price} at {venue.name}. Would I come back? {opinion}",
                  card="Would I come back? {opinion}", caption="{menuItem.name} · {menuItem.price}",
                  opinion={"set": "verdict_answer", "preselect": None, "order": ["certainly", "maybe", "not_for_me"]},
                  noPrice={"line": "{venue.name}. Would I come back? {opinion}",
                           "card": "Would I come back? {opinion}", "caption": "{menuItem.name}"})
        self.assertEqual(rules(**ok) - {"L9-caption"}, set())
        self.assertEqual(rules(line="Asking what first-timers order.", caption="The order"), set())
        self.assertEqual(rules(line="Picking from the menu.", caption="The menu"), set())

    def test_sets_pass(self):
        self.assertEqual(line_lint.set_rules(SETS), [])

    def test_set_rules_catch(self):
        bad = {"x": {"id": "x", "kind": "verdict", "maxWords": 2, "allowCustom": False, "preselectAllowed": True,
                     "options": [{"id": "a", "text": "The best in town.", "tone": "positive"}]}}
        messages = " ".join(m for _, _, m in line_lint.set_rules(bad))
        for part in ("no neutral option", "allowCustom", "never allows a preselection", "private_feedback", "L12"):
            self.assertIn(part, messages)


class TypedDish(unittest.TestCase):
    TYPED = {"id": "food-review-typed", "venueKinds": ["coffee"], "featuresMenuItem": True,
             "dishSource": {"kind": "typed", "maxLength": 40, "hint": "The dish or drink you are reviewing"}, "steps": []}

    def test_typed_never_has_a_price(self):
        s = dict(copy.deepcopy(BASE), line="{menuItem.price} for {menuItem.name}.", caption="{menuItem.name}")
        t = dict(self.TYPED, steps=[s])
        self.assertIn("L6", {r for r, _, _ in line_lint.step_rules(t, s, SETS, True)})

    def test_typed_name_is_timed_at_its_cap(self):
        name = line_lint.sample(self.TYPED)["menuItem.name"]
        self.assertTrue(30 <= len(name) <= 40, name)
        s = dict(copy.deepcopy(BASE), line="{venue.name}. I came here for one thing: {menuItem.name}.", caption="{venue.name}")
        t = dict(self.TYPED, steps=[s])
        self.assertIn("L9", {r for r, _, _ in line_lint.step_rules(t, s, SETS, True)})

    def test_dish_source_shape(self):
        menu = {"id": "food-review", "venueKinds": ["coffee", "dining"], "featuresMenuItem": True,
                "dishSource": {"kind": "menu", "whenNoMenu": "food-review-typed"}, "steps": []}
        self.assertEqual(line_lint.dish_source_rules([menu, dict(self.TYPED, venueKinds=["coffee", "dining"])]), [])
        bad = dict(self.TYPED, dishSource={"kind": "typed", "maxLength": 200, "hint": "{venue.name}"})
        messages = " ".join(m for _, _, m, _ in line_lint.dish_source_rules([menu, bad]))
        for part in ("maxLength 200", "no placeholders", "does not cover venue kinds"):
            self.assertIn(part, messages)

    def test_menu_with_typed_fallback(self):
        fv = {"id": "first-visit", "venueKinds": ["coffee", "dining"], "featuresMenuItem": True,
              "dishSource": {"kind": "menu", "typedFallback": {"maxLength": 40, "hint": "The dish or drink you are ordering"}},
              "steps": []}
        self.assertEqual(line_lint.dish_source_rules([fv]), [])
        self.assertTrue(30 <= len(line_lint.sample(fv)["menuItem.name"]) <= 40)
        s = dict(copy.deepcopy(BASE), line="{menuItem.price} for {menuItem.name}.", caption="{menuItem.name}")
        self.assertIn("L6", {r for r, _, _ in line_lint.step_rules(dict(fv, steps=[s]), s, SETS, True)})
        both = dict(fv, dishSource={"kind": "menu", "whenNoMenu": "x", "typedFallback": {"maxLength": 99, "hint": ""}})
        messages = " ".join(m for _, _, m, _ in line_lint.dish_source_rules([both]))
        for part in ("not both", "maxLength 99", "hint is required"):
            self.assertIn(part, messages)


if __name__ == "__main__":
    unittest.main()
