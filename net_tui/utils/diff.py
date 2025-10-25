import difflib

  def unified_diff(old_text: str, new_text: str, fromfile="old", tofile="new") -> str:
    old = old_text.splitlines(keepends=True)
    new = new_text.splitlines(keepends=True)
    return "".join(difflib.unified_diff(old, new, fromfile, tofile))
