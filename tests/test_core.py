import os
import tempfile
import unittest

from file_line_counter_lib import LineCountResult, count_lines
from file_line_counter_lib.core import _count_stream


class CountLinesTests(unittest.TestCase):
    def setUp(self) -> None:
        fd, self.path = tempfile.mkstemp(prefix="flc_", suffix=".txt")
        os.close(fd)

    def tearDown(self) -> None:
        if os.path.exists(self.path):
            os.remove(self.path)

    def _write(self, text: str) -> None:
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def test_plain_file_no_trailing_newline(self) -> None:
        self._write("a\nb\nc")
        result = count_lines(self.path)
        self.assertEqual(result, LineCountResult(total=3, effective=3))

    def test_plain_file_with_trailing_newline(self) -> None:
        self._write("a\nb\nc\n")
        result = count_lines(self.path)
        self.assertEqual(result.total, 3)
        self.assertEqual(result.effective, 3)

    def test_empty_file(self) -> None:
        self._write("")
        result = count_lines(self.path)
        self.assertEqual(result.total, 0)
        self.assertEqual(result.effective, 0)

    def test_only_newlines(self) -> None:
        self._write("\n\n\n")
        result = count_lines(self.path)
        self.assertEqual(result.total, 3)
        self.assertEqual(result.effective, 3)

    def test_skip_blank(self) -> None:
        self._write("a\n\nb\n   \nc\n")
        result = count_lines(self.path, skip_blank=True)
        self.assertEqual(result.total, 5)
        self.assertEqual(result.effective, 3)

    def test_skip_comments(self) -> None:
        self._write("# header\na\n  # indented\nb\n")
        result = count_lines(self.path, skip_comments=True)
        self.assertEqual(result.total, 4)
        self.assertEqual(result.effective, 2)

    def test_skip_blank_and_comments(self) -> None:
        self._write("# header\n\na\n   \n  # note\nb\n")
        result = count_lines(self.path, skip_blank=True, skip_comments=True)
        self.assertEqual(result.total, 6)
        self.assertEqual(result.effective, 2)

    def test_comment_only_line_classified_as_comment(self) -> None:
        """A line that is just '#' is a comment, not blank."""
        self._write("#\na\n")
        result = count_lines(self.path, skip_blank=True, skip_comments=True)
        self.assertEqual(result.total, 2)
        self.assertEqual(result.effective, 1)

    def test_carriage_return_line_endings(self) -> None:
        self._write("a\rb\rc")
        result = count_lines(self.path)
        self.assertEqual(result.total, 3)

    def test_blank_with_tabs(self) -> None:
        self._write("\t\t\na\n")
        result = count_lines(self.path, skip_blank=True)
        self.assertEqual(result.total, 2)
        self.assertEqual(result.effective, 1)

    def test_nonexistent_file_raises(self) -> None:
        missing = os.path.join(os.path.dirname(self.path), "does_not_exist_xyz")
        with self.assertRaises(FileNotFoundError):
            count_lines(missing)

    def test_directory_raises(self) -> None:
        with self.assertRaises(IsADirectoryError):
            count_lines(os.path.dirname(self.path))

    def test_stream_directly(self) -> None:
        import io

        result = _count_stream(
            io.StringIO("a\n# b\n\nc\n"),
            skip_blank=True,
            skip_comments=True,
        )
        self.assertEqual(result.total, 4)
        self.assertEqual(result.effective, 2)


if __name__ == "__main__":
    unittest.main()
