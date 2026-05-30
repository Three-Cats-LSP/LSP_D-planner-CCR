# Contributing

## Algorithm bugs

The highest-value contributions are algorithm accuracy reports. If LSP produces a plan that differs significantly from another reference planner, open an issue with:

- Dive parameters (depth, BT, gas, GF, water type)
- LSP output
- Reference planner output (name + version)
- Your analysis of which is more correct, with sources if possible

## Code contributions

The app is a single `index.html` file. Keep it that way — the single-file design is intentional (offline use, easy distribution, no build step).

Before submitting a PR:
- Test on Chrome, Firefox, and Safari mobile
- Verify the deco schedule output hasn't regressed against the reference table in README.md
- Do not add external dependencies

## What not to contribute

- New features before existing bugs are fixed
- UI redesigns without discussion
- Documentation that duplicates what's already in README.md
