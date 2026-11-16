"""Tests for the catalog v3 checker. Run: python3 -I scripts/tools/test_v3.py"""
import copy
import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v3_catalog as V  # noqa: E402


class V3Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables, cls.sets, cls.scripts = V.load_all()

    def run_with(self, mutate, sets=None):
        scripts = copy.deepcopy(self.scripts)
        sets_ = copy.deepcopy(sets or self.sets)
        mutate(scripts, sets_)
        errors, _, _, _ = V.check(self.tables, sets_, scripts)
        return errors

    def step(self, scripts, kind, key):
        return next(s for s in next(x for x in scripts if x["kind"] == kind)["steps"] if s["key"] == key)

    def has(self, errors, code):
        return any(f" {code} " in e or f": {code}" in e for e in errors)

    def test_catalog_is_clean(self):
        errors, _, _, _ = V.check(self.tables, self.sets, self.scripts)
        self.assertEqual(errors, [])

    def test_judgement_outside_slot(self):
        def m(s, _):
            self.step(s, "dish-review", "arrive")["versions"][0]["line"] = "{venue.name}. The coffee is amazing."
        self.assertTrue(self.has(self.run_with(m), "L3"))

    def test_hearsay(self):
        def m(s, _):
            self.step(s, "dish-review", "arrive")["versions"][0]["line"] = "Everyone keeps telling me about {venue.name}."
        self.assertTrue(self.has(self.run_with(m), "L1"))

    def test_time_word_needs_daypart_tag(self):
        def m(s, _):
            self.step(s, "dish-review", "arrive")["versions"][0]["line"] = "Lunch at {venue.name}."
        self.assertTrue(self.has(self.run_with(m), "L5"))

    def test_time_word_allowed_when_tagged(self):
        def m(s, _):
            ver = self.step(s, "dish-review", "arrive")["versions"][0]
            ver["line"], ver["tags"] = "Lunch at {venue.name}.", {"daypart": "midday"}
        self.assertFalse(self.has(self.run_with(m), "L5"))

    def test_price_only_in_price_variant(self):
        def m(s, _):
            self.step(s, "dish-review", "verdict")["versions"][0]["line"] = "{menuItem.price}. Would I come back? {opinion}"
        self.assertTrue(any("L6/L10" in e for e in self.run_with(m)))

    def test_verdict_never_preselected(self):
        def m(s, _):
            self.step(s, "dish-review", "verdict")["choice"]["preselect"] = 3
        self.assertTrue(self.has(self.run_with(m), "V7"))

    def test_three_levels(self):
        def m(_, sets):
            sets["verdict_dish"]["levels"].pop()
        self.assertTrue(self.has(self.run_with(m), "V6"))

    def test_no_negative_level(self):
        def m(_, sets):
            sets["bite_savory"]["levels"][0]["tone"] = "negative"
        self.assertTrue(self.has(self.run_with(m), "V6"))

    def test_not_for_me_only_on_verdicts(self):
        def m(_, sets):
            sets["bite_savory"]["privateFeedback"] = {"label": "Not for me", "action": "private_feedback"}
        self.assertTrue(self.has(self.run_with(m), "V7"))

    def test_not_for_me_required_on_verdict(self):
        def m(_, sets):
            sets["verdict_dish"].pop("privateFeedback")
        self.assertTrue(self.has(self.run_with(m), "V7"))

    def test_form_is_not_a_when_key(self):
        def m(s, _):
            self.step(s, "drink-review", "main")["variants"][0]["when"] = {"form": "glass"}
        self.assertTrue(self.has(self.run_with(m), "V4"))

    def test_no_step_pictures(self):
        def m(s, _):
            self.step(s, "dish-review", "arrive")["imageURL"] = "dish-review_arrive.jpg"
        self.assertTrue(any("no pictures" in e for e in self.run_with(m)))

    def test_version_pool_size(self):
        def m(s, _):
            self.step(s, "dish-review", "arrive")["versions"] = self.step(s, "dish-review", "arrive")["versions"][:2]
        self.assertTrue(self.has(self.run_with(m), "V3"))

    def test_visit_outcome_claim(self):
        def m(s, _):
            var = next(v for v in self.step(s, "venue-review", "after")["variants"] if v["when"].get("subject") == "visit")
            var["versions"][0]["line"] = "They cured my back pain."
        self.assertTrue(self.has(self.run_with(m), "V9"))

    def test_visit_needs_no_clients_direction(self):
        def m(s, _):
            var = next(v for v in self.step(s, "venue-review", "main")["variants"] if v["when"].get("subject") == "visit")
            var["direction"] = "Film the treatment."
        self.assertTrue(self.has(self.run_with(m), "V9"))

    def test_call_to_action_in_authored_text(self):
        def m(s, _):
            self.step(s, "venue-review", "arrive")["versions"][0]["line"] = "Go visit {venue.name}."
        self.assertTrue(self.has(self.run_with(m), "L4"))

    def test_alcohol_is_p1(self):
        tables = copy.deepcopy(self.tables)
        next(k for k in tables["drinkKinds"] if k["id"] == "cocktails")["phase"] = "P0"
        errors = []
        V.check_tables(tables, errors)
        self.assertTrue(self.has(errors, "V10"))

    def test_amenity_non_smoking_not_a_chip(self):
        def m(_, sets):
            sets["amenities"]["options"].append({"slug": "non_smoking", "text": "Non-smoking", "tone": "neutral"})
        self.assertTrue(self.has(self.run_with(m), "V6"))

    def test_line_too_long_with_real_values(self):
        def m(s, _):
            self.step(s, "dish-review", "arrive")["versions"][0]["line"] = (
                "{venue.name}. I came here today after a long walk across town for {menuItem.name} and a seat.")
        self.assertTrue(any("L8/L9" in e for e in self.run_with(m)))

    def test_silent_step_has_no_line(self):
        def m(s, _):
            self.step(s, "dish-review", "main")["versions"][0]["line"] = "Here it is."
        self.assertTrue(self.has(self.run_with(m), "L7"))

    def test_menu_section_mapping(self):
        self.assertEqual(V.menu_kind("Cocktails", self.tables), ("drink-review", "cocktails"))
        self.assertEqual(V.menu_kind("Сніданки", self.tables), ("dish-review", "breakfast"))
        self.assertEqual(V.menu_kind("Specials", self.tables), ("dish-review", None))

    def test_first_matching_variant_wins(self):
        step = self.step(self.scripts, "drink-review", "after")
        self.assertEqual(V.effective_step(step, {"drinkKind": "tea-matcha"})["choice"]["set"], "sip_tea")
        self.assertEqual(V.effective_step(step, {})["choice"]["set"], "sip_coffee")

    def test_written_versions_checked(self):
        script = next(x for x in self.scripts if x["kind"] == "dish-review")
        bad = V.written_errors(script, "arrive", [{"line": "The best spot in town.", "card": "Best", "caption": "{venue.name}"}],
                               {}, self.sets, self.tables)
        self.assertTrue(bad)

    def test_client_catalog_has_no_gap(self):
        errors, warnings, timing, guides = V.check(self.tables, self.sets, self.scripts)
        catalog = V.build(self.tables, self.sets, self.scripts, timing, guides)
        self.assertNotIn('"gap"', json.dumps(catalog))
        self.assertNotIn('"noGuideAllowed"', json.dumps(catalog))
        for script in catalog["kinds"]:
            for step in script.get("steps") or []:
                self.assertIsInstance(step.get("guides", []), list)

    def test_open_gap_variant_does_not_inherit_base_guides(self):
        step = self.step(self.scripts, "venue-review", "before")
        self.assertEqual(V.effective_step(step, {"subject": "result"})["guides"], [])
        self.assertEqual(V.effective_step(step, {"subject": "visit"})["guides"], ["visit_front_desk_hello"])

    def test_frozen_kinds(self):
        errors = []
        V.check_frozen_kinds(self.tables, errors)
        self.assertEqual(errors, [])
        renamed = copy.deepcopy(self.tables)
        renamed["dishKinds"][0]["id"] = "starters"
        errors = []
        V.check_frozen_kinds(renamed, errors)
        self.assertTrue(any("removed or renamed" in e for e in errors) and any("new id" in e for e in errors))
        deprecated = copy.deepcopy(self.tables)
        deprecated["drinkKinds"][0]["deprecated"] = True
        errors = []
        V.check_frozen_kinds(deprecated, errors)
        self.assertTrue(any("replacedBy" in e for e in errors))
        deprecated["drinkKinds"][0]["replacedBy"] = "tea-matcha"
        errors = []
        V.check_frozen_kinds(deprecated, errors)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
