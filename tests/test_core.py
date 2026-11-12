"""Tests for natural_sort_kit.core.

Run with: PYTHONPATH=src python -m unittest discover -s tests
"""

import unittest

from natural_sort_kit import natural_key, natural_sorted


class NaturalKeyTests(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(natural_key(""), ())

    def test_text_only(self):
        # One text chunk, keyed by (lowercased, original).
        self.assertEqual(natural_key("apple"), ((1, ("apple", "apple")),))

    def test_number_only(self):
        self.assertEqual(natural_key("10"), ((0, 10),))

    def test_mixed(self):
        self.assertEqual(
            natural_key("file10.txt"),
            ((1, ("file", "file")), (0, 10), (1, (".txt", ".txt"))),
        )

    def test_leading_digit(self):
        self.assertEqual(natural_key("2fast"), ((0, 2), (1, ("fast", "fast"))))

    def test_multiple_numbers(self):
        self.assertEqual(
            natural_key("a1b2"),
            (
                (1, ("a", "a")),
                (0, 1),
                (1, ("b", "b")),
                (0, 2),
            ),
        )

    def test_type_error_on_non_str(self):
        with self.assertRaises(TypeError):
            natural_key(123)  # type: ignore[arg-type]


class NaturalSortedTests(unittest.TestCase):
    def test_file2_before_file10(self):
        names = ["file10", "file2", "file1"]
        self.assertEqual(natural_sorted(names), ["file1", "file2", "file10"])

    def test_case_insensitive_primary(self):
        # "Apple" and "apple" differ only by case; lowercased text ties, so the
        # original casing breaks the tie.  Uppercase sorts before lowercase.
        self.assertEqual(natural_sorted(["apple", "Apple"]), ["Apple", "apple"])

    def test_reverse(self):
        names = ["file2", "file10", "file1"]
        self.assertEqual(
            natural_sorted(names, reverse=True), ["file10", "file2", "file1"]
        )

    def test_leading_zeros(self):
        # "007" and "7" both parse to 7, so the numeric chunk ties; the
        # remaining text chunks (none here) decide.  They are equal as keys,
        # which means Python's stable sort preserves input order.
        result = natural_sorted(["007", "7"])
        self.assertEqual(result, ["007", "7"])
        result = natural_sorted(["7", "007"])
        self.assertEqual(result, ["7", "007"])

    def test_numeric_before_text(self):
        # At the same position, numeric chunks rank before text chunks.
        self.assertEqual(natural_sorted(["a", "1"]), ["1", "a"])

    def test_empty_and_non_empty(self):
        self.assertEqual(natural_sorted(["b", "", "a"]), ["", "a", "b"])

    def test_unicode_text_chunks(self):
        # We do not normalise Unicode; code points are compared directly.
        self.assertEqual(natural_sorted(["café", "cafe"]), ["cafe", "café"])

    def test_returns_list(self):
        out = natural_sorted(("b1", "a1"))
        self.assertIsInstance(out, list)
        self.assertEqual(out, ["a1", "b1"])

    def test_does_not_mutate_input(self):
        names = ["b2", "a1"]
        natural_sorted(names)
        self.assertEqual(names, ["b2", "a1"])


if __name__ == "__main__":
    unittest.main()
