import json
import tempfile
import unittest
from pathlib import Path

from proseguard import Linter, Config, load_config


class EngineTests(unittest.TestCase):
    def test_catalog_has_20_rules(self):
        catalog = Linter.catalog()
        self.assertEqual(len(catalog), 20)
        ids = {r["id"] for r in catalog}
        self.assertEqual(len(ids), 20)

    def test_disable_rule(self):
        result = Linter(Config(disable={"PG100"})).lint_text(
            "This is definately wrong.")
        self.assertFalse(any(f.rule_id == "PG100" for f in result.findings))

    def test_enable_only(self):
        result = Linter(Config(enable={"PG100"})).lint_text(
            "This is definately,  very wrong indeed.")
        ids = {f.rule_id for f in result.findings}
        self.assertEqual(ids, {"PG100"})

    def test_unknown_rule_raises(self):
        with self.assertRaises(ValueError):
            Linter(Config(enable={"PG999"}))

    def test_findings_sorted_by_offset(self):
        result = Linter().lint_text("definately and recieve")
        offsets = [f.start for f in result.findings]
        self.assertEqual(offsets, sorted(offsets))

    def test_markdown_code_protected(self):
        text = ("Outside definately.\n```\nrecieve teh seperate\n```\n"
                "Inside `recieve` ignored.")
        result = Linter().lint_text(text)
        bad = [f for f in result.findings if f.rule_id == "PG100"]
        # Only "definately" outside the fence/inline code is reported.
        self.assertEqual(len(bad), 1)
        self.assertEqual(bad[0].replacement, "definitely")

    def test_positions_map_to_raw(self):
        text = "Line one.\nThis is definately it."
        result = Linter().lint_text(text)
        f = next(f for f in result.findings if f.rule_id == "PG100")
        sl, sc, _, _ = f.position(text)
        self.assertEqual(sl, 2)
        self.assertEqual(text.splitlines()[sl - 1][sc - 1:sc - 1 + len(f.excerpt)],
                         "definately")


class ConfigFileTests(unittest.TestCase):
    def test_loads_from_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".proseguard.json").write_text(json.dumps({
                "disable": ["PG400"],
                "personal_dictionary": ["foobar"],
                "max_sentence_words": 33,
            }))
            cfg = load_config(search_from=Path(tmp))
            self.assertIn("PG400", cfg.disable)
            self.assertIn("foobar", cfg.personal_dictionary)
            self.assertEqual(cfg.max_sentence_words, 33)

    def test_missing_explicit_config_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_config(explicit="/nonexistent/proseguard.json")


if __name__ == "__main__":
    unittest.main()
