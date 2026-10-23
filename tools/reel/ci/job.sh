bash tools/reel/ci/$(cat tools/reel/ci/MODE)
# 23.10: a mode script that edits tracked files (NAMES, specs) makes the publish rebase fail and ALL outputs are lost. Always restore them.
git checkout -- tools/reel/ci/NAMES tools/reel/specs 2>/dev/null || true
