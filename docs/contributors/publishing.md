# Publishing a release

Releases are manual. Run these commands from the repository root, stopping if a
command fails. The order is: prepare, check, commit, build, tag, publish to PyPI,
then create the GitHub Release.

## Setup

Install the development tools with `mise install` and install the GitHub CLI
(`gh`). Authenticate once with `gh auth login`. Keep `UV_PUBLISH_TOKEN` in the
local `.env`; `mise exec --` loads it without putting the token in commands.

Python packages go to PyPI. GitHub Releases hold downloadable artifacts;
[GitHub Packages](https://docs.github.com/en/packages/working-with-a-github-packages-registry)
does not provide a Python registry.

## 1. Prepare the version and changelog

Finish the code, README, and documentation first. To prepare the next patch
release:

```bash
mise exec -- uv version --package formulens --bump patch --no-sync
```

Set the version and tag for the remaining commands in the same terminal:

```bash
FORMULENS_VERSION=$(mise exec -- uv version --package formulens --short)
FORMULENS_TAG="formulens-v$FORMULENS_VERSION"
```

Update `packages/formulens/CHANGELOG.md` by hand:

- Add short, user-facing changes under `Unreleased`, grouped as Added, Changed, or Fixed when useful.
- Before releasing, rename that section to the version and release date, for example `0.1.0 — YYYY-MM-DD`.
- Keep previous versions below it, newest first. Start a new `Unreleased` section when work resumes.

Each package keeps its own changelog. Record meaningful behavior changes rather
than every commit; omit empty categories.

## 2. Check and commit

Run the checks and verify representative equation captures on your NVIDIA GPU:

```bash
mise exec -- uv sync --locked --package formulens
mise exec -- uv run --no-sync python -m unittest discover -s tests
mise exec -- prek run --all-files
mise exec -- uvx zensical build --clean
```

If hooks modify files, review them and rerun the checks. Review `git diff`, stage
the intended release changes, and commit them. Confirm `git status --short` is
empty and that you are on `main` before proceeding.

## 3. Build and inspect

Use a version-specific output directory and publish only the two named artifacts:

```bash
FORMULENS_DIST="dist/formulens/$FORMULENS_VERSION"
FORMULENS_WHEEL="$FORMULENS_DIST/formulens-$FORMULENS_VERSION-py3-none-any.whl"
FORMULENS_SDIST="$FORMULENS_DIST/formulens-$FORMULENS_VERSION.tar.gz"
mise exec -- uv build --package formulens --out-dir "$FORMULENS_DIST"
mise exec -- uv run --no-project --with "$FORMULENS_WHEEL" formulens --help
mise exec -- uv publish --dry-run "$FORMULENS_WHEEL" "$FORMULENS_SDIST"
```

Inspect the wheel/source archive and README before uploading. The dry run uploads
nothing; it does not prove that PyPI will accept the credentials or publication.

## 4. Push and tag the reviewed commit

```bash
git push origin main
git tag -a "$FORMULENS_TAG" -m "Formulens $FORMULENS_VERSION"
git push origin "$FORMULENS_TAG"
```

Copy only this version's changelog section into
`$FORMULENS_DIST/release-notes.md` for the GitHub Release description. This is a
local build file, not another documentation page. Pushing the tag does not
automatically publish the package.

## 5. Publish to PyPI

```bash
mise exec -- uv publish --check-url https://pypi.org/simple "$FORMULENS_WHEEL" "$FORMULENS_SDIST"
```

Confirm the version and README on [PyPI](https://pypi.org/project/formulens/).

## 6. Create the GitHub Release

Use the same artifacts and the package changelog:

```bash
gh release create "$FORMULENS_TAG" --verify-tag \
  --title "Formulens $FORMULENS_VERSION" \
  --notes-file "$FORMULENS_DIST/release-notes.md" \
  "$FORMULENS_WHEEL" "$FORMULENS_SDIST" packages/formulens/CHANGELOG.md
```

For an alpha, beta, or release candidate, add `--prerelease`. These options are
explained in the [GitHub CLI manual](https://cli.github.com/manual/gh_release_create).

## If an upload fails

Keep the same tagged commit and built artifacts. Repeat the PyPI command;
`--check-url` skips files already uploaded. If the GitHub Release already exists,
check its assets and use `gh release upload "$FORMULENS_TAG" <missing-file>` to
add a missing asset. See the [upload manual](https://cli.github.com/manual/gh_release_upload).

A transient upload failure does not require a version bump. Changes to the
published package contents do require a new version; do not move a published tag.
