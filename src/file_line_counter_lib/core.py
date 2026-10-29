"""Line counting for files, streamed one line at a time.

The module exposes :func:`count_lines`, which reads a file line by line so
that arbitrarily large files can be counted without holding them in memory.
Lines are decoded as UTF-8 with ``errors="replace"`` so that binary or
malformed input still yields a deterministic count rather than raising.

A line is considered *blank* when, after stripping leading and trailing
ASCII whitespace, it is empty.  A line is considered a *comment* when its
first non-whitespace character is ``#``.  These are the two conventions most
source files follow; the interpretation is deliberately narrow so that
behaviour is predictable.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import IO


@dataclass(frozen=True)
class LineCountResult:
    """Outcome of a line count.

    ``total`` is the number of lines actually present in the file, while
    ``effective`` is the number remaining after any requested filters are
    applied.  When no filters are requested the two values are equal.
    """

    total: int
    effective: int


def _is_blank(line: str) -> bool:
    """Return True when *line* has no non-whitespace content."""
    return len(line.strip()) == 0


def _is_comment(line: str) -> bool:
    """Return True when *line*'s first non-whitespace character is '#'.

    Tested before blank-checking so that a line containing only ``#`` is
    treated as a comment rather than blank.
    """
    return line.lstrip().startswith("#")


def count_lines(
    path: str | os.PathLike[str],
    *,
    skip_blank: bool = False,
    skip_comments: bool = False,
) -> LineCountResult:
    """Count lines in the file at *path*.

    The file is opened in text mode with ``encoding="utf-8"`` and
    ``errors="replace"`` and iterated one line at a time, so peak memory is
    bounded by the longest line rather than the file size.

    Parameters
    ----------
    path:
        File to read.
    skip_blank:
        When True, lines that are empty after stripping whitespace are
        excluded from ``effective``.
    skip_comments:
        When True, lines whose first non-whitespace character is ``#`` are
        excluded from ``effective``.

    Returns
    -------
    LineCountResult
        ``total`` counts every line; ``effective`` counts the subset that
        survives the filters.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    IsADirectoryError
        If *path* is a directory.
    OSError
        Other I/O errors from the underlying open/read.
    """
    return _count_from_file(
        path,
        skip_blank=skip_blank,
        skip_comments=skip_comments,
    )


def _count_from_file(
    path: str | os.PathLike[str],
    *,
    skip_blank: bool,
    skip_comments: bool,
) -> LineCountResult:
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
        return _count_stream(
            fh,
            skip_blank=skip_blank,
            skip_comments=skip_comments,
        )


def _count_stream(
    stream: IO[str],
    *,
    skip_blank: bool,
    skip_comments: bool,
) -> LineCountResult:
    total = 0
    effective = 0
    for line in stream:
        total += 1
        if skip_comments and _is_comment(line):
            continue
        if skip_blank and _is_blank(line):
            continue
        effective += 1
    return LineCountResult(total=total, effective=effective)
