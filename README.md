# Wellog Visualization Skill Documentation

This repository maintains the documentation and examples for the `wellog-viz` skill, based on the [videx-wellog](https://github.com/equinor/videx-wellog) library.

## Project Structure

- `SKILL.md`: Main entry point for the skill description.
- `references/`: Detailed examples and data snippets.
- `upstream-src/`: A git submodule pointing to the `videx-wellog` source code. This is used as a reference to ensure documentation stays up-to-date with the library.

## Maintenance Workflow

### Updating Source Reference

To pull the latest changes from the upstream `videx-wellog` repository:

```bash
git submodule update --remote --merge
```

This updates the `upstream-src` folder to the latest commit on the default branch of the upstream repo. You can then inspect the code in `upstream-src` to verify API changes or new features.

### Updating Documentation

1. Check `upstream-src` for changes.
2. Update `SKILL.md` or files in `references/` accordingly.
3. Commit your changes:

```bash
git add .
git commit -m "Update docs based on upstream changes"
```
