# History

One line per retired slice, oldest first. Detail lives in the completed slice file; this is the narrative index.

Format: `YYYY-MM-DD - NNN title - what shipped - ADRs touched - divergence from plan`

2026-09-17 - 001 Set up the Python toolchain and the check gate - `make check` running ruff then pytest, green in CI on a clean clone - 0001, 0005, neither changed - ruff 0.16 formats Markdown so `*.md` is excluded, and `setup-uv` has no `v10` tag so it is pinned to `v10.1.0`
