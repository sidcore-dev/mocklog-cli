import io
import json
import unittest
from contextlib import redirect_stdout

from mocklog_cli.cli import main


class TestCli(unittest.TestCase):
    def test_default_count_is_100(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["--seed", "1"])
        self.assertEqual(code, 0)
        lines = out.getvalue().splitlines()
        self.assertEqual(len(lines), 100)

    def test_custom_count(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            main(["--count", "5", "--seed", "1"])
        lines = out.getvalue().splitlines()
        self.assertEqual(len(lines), 5)

    def test_combined_format_default(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            main(["--count", "3", "--seed", "1"])
        line = out.getvalue().splitlines()[0]
        self.assertRegex(line, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z \[[A-Z]+\] [\w-]+: .+$")

    def test_json_format(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            main(["--count", "3", "--format", "json", "--seed", "1"])
        for line in out.getvalue().splitlines():
            data = json.loads(line)
            self.assertIn("timestamp", data)
            self.assertIn("level", data)

    def test_levels_flag_restricts_output(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out):
            main(["--count", "20", "--levels", "ERROR", "--seed", "1"])
        for line in out.getvalue().splitlines():
            self.assertIn("[ERROR]", line)

    def test_invalid_count_returns_error(self) -> None:
        code = main(["--count", "0"])
        self.assertEqual(code, 2)

    def test_invalid_levels_returns_error(self) -> None:
        code = main(["--levels", "NOTALEVEL"])
        self.assertEqual(code, 2)

    def test_seed_gives_reproducible_output(self) -> None:
        out_a, out_b = io.StringIO(), io.StringIO()
        with redirect_stdout(out_a):
            main(["--count", "10", "--seed", "99"])
        with redirect_stdout(out_b):
            main(["--count", "10", "--seed", "99"])
        self.assertEqual(out_a.getvalue(), out_b.getvalue())


if __name__ == "__main__":
    unittest.main()
