# file_line_counter_lib

Counts lines in a file without loading the whole file into memory, with optional filtering of blank and comment lines.

```python
import tempfile, os
from file_line_counter_lib import count_lines

# build a small file: code line, blank line, code line
fd, path = tempfile.mkstemp(suffix=".txt")
os.write(fd, "code line\n\ncode line\n".encode())
os.close(fd)

result = count_lines(path)
print(result.total, result.effective)  # 3 3

result = count_lines(path, skip_blank=True, skip_comments=True)
print(result.effective)  # 2
```

`count_lines(path, *, skip_blank=False, skip_comments=False)` returns a `LineCountResult` with two integers: `total` (every line in the file) and `effective` (the subset that survives the filters). The file is opened as UTF-8 and iterated one line at a time, so memory use is bounded by the longest line rather than the file size.

The library exists for the common case of reporting "lines of code" over files that may be too large to read into a list. The trade-off is simplicity: only two filtering conventions are supported — a blank line is one that is empty after stripping whitespace, and a comment line is one whose first non-whitespace character is `#`. If your files use a different comment marker or multi-line comments, this library will not handle them.

The edge you will hit: a line containing only `#` is treated as a comment, not as blank, so with both `skip_blank=True` and `skip_comments=True` it is excluded exactly once. Files without a trailing newline still count their final line. Malformed bytes are replaced rather than raising, so binary input produces a deterministic count.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

