import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"


def run_cli(*args, input_text=None):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [sys.executable, "-m", "proseguard", *args],
        input=input_text, capture_output=True, text=True, env=env,
        cwd=str(ROOT),
    )
    return proc


class CliTests(unittest.TestCase):
    def test_version(self):
        p = run_cli("--version")
        self.assertEqual(p.returncode, 0)
        self.assertIn("1.0.0", p.stdout)

    def test_list_rules(self):
        p = run_cli("--list-rules")
        self.assertEqual(p.returncode, 0)
        self.assertIn("PG100", p.stdout)
        self.assertIn("PG500", p.stdout)

    def test_bad_file_exit_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "bad.txt")
            f.write_text("This is definately wrong.")
            p = run_cli(str(f), "--color", "never")
            self.assertEqual(p.returncode, 1)
            self.assertIn("PG100", p.stdout)

    def test_clean_file_exit_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "good.txt")
            f.write_text("A perfectly clean and simple sentence.")
            p = run_cli(str(f))
            self.assertEqual(p.returncode, 0)

    def test_stdin(self):
        p = run_cli("-", input_text="This is definately wrong.")
        self.assertEqual(p.returncode, 1)
        self.assertIn("PG100", p.stdout)

    def test_fix_in_place(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "fix.txt")
            f.write_text("This is definately wrong.")
            p = run_cli("--fix", str(f))
            self.assertIn(p.returncode, (0, 1))
            self.assertIn("definitely", f.read_text())
            self.assertNotIn("definately", f.read_text())

    def test_json_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "bad.md")
            f.write_text("This is definately wrong.")
            p = run_cli("-f", "json", str(f))
            payload = json.loads(p.stdout)
            self.assertIn("files", payload)
            self.assertEqual(payload["summary"]["error"], 1)

    def test_unknown_rule_exit_2(self):
        p = run_cli("--enable", "PG999", ".")
        self.assertEqual(p.returncode, 2)

    def test_directory_scan_with_exclude(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "ok.txt").write_text("Clean sentence here.")
            skip = Path(tmp, "draft")
            skip.mkdir()
            (skip / "bad.txt").write_text("definately wrong")
            p = run_cli(tmp, "--exclude", "draft")
            self.assertEqual(p.returncode, 0)

    def test_html_report_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp, "bad.txt")
            src.write_text("This is definately wrong.")
            out = Path(tmp, "report.html")
            p = run_cli("-f", "html", "-o", str(out), str(src))
            self.assertEqual(p.returncode, 1)
            self.assertTrue(out.is_file())
            self.assertIn("<!DOCTYPE html>", out.read_text())


if __name__ == "__main__":
    unittest.main()
