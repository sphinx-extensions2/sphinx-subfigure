# Changelog

## v0.3.0 - 2026-07-12

Modernization and bug-fix release.

### ⬆️ Upgrade

- Python 3.11+ and Sphinx 8/9 are now required (previously Python 3.7+) ([#21](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/21))

### ✨ New

- Support parallel reading and writing, so `sphinx-build -j auto` can parallelize projects using this extension; the extension version is also now reported correctly in tracebacks ([#28](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/28), thanks to @Bizordec)
- Figure captions can now be localized ([#14](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/14), thanks to Jan Breuer)

### 🐛 Fixes

- LaTeX: layouts that are not a simple `A→B→C` progression (e.g. `B|A`) crashed the build with an `IndexError`; they now fall back to a plain figure, as documented ([#23](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/23), reported in [#17](https://github.com/sphinx-extensions2/sphinx-subfigure/issues/17))
- LaTeX: multi-row (vertical) spans beginning after an empty `.` cell (e.g. `.A|.A`) silently produced overfull subfigure widths; they now also fall back to a plain figure ([#23](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/23))
- HTML: responsive media-query CSS is now emitted in ascending breakpoint order, so with multiple figures on a page a narrower layout can no longer override a wider one ([#23](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/23))
- Removed stray debug output printed to stdout on every build ([#28](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/28), thanks to @andersfagerli, reported in [#18](https://github.com/sphinx-extensions2/sphinx-subfigure/issues/18))
- Spaces in layout strings are now ignored (previously they failed validation), so they can be used for visual alignment ([#23](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/23))
- `.. subfigure:: 0` no longer aborts the build with `ZeroDivisionError` ([#23](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/23))
- Unitless `:gap:` values now default to `px` (a unitless `gap` is invalid CSS that browsers silently drop) ([#23](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/23))
- reStructuredText comments inside the directive content are now ignored, instead of aborting the figure ([#23](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/23))
- Non-whitespace text in a MyST image paragraph now raises a clear error, instead of being silently discarded ([#23](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/23))
- More than 26 images, and subfigures containing no images, now raise clear directive errors instead of crashing or giving misleading messages ([#23](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/23))
- LaTeX subfigure widths no longer contain floating-point artifacts ([#23](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/23))

### 🔧 Maintenance

- Lint/format with ruff (replacing black/isort/flake8/pyupgrade) ([#21](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/21))
- CI: test matrix of Python 3.11–3.14 × Sphinx 8/9 (Ubuntu and Windows), and PyPI trusted publishing on version tags ([#21](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/21))
- Fixed the Read the Docs build (now-mandatory `configuration` key) ([#21](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/21))
- Added `AGENTS.md` guidance for contributors and AI coding agents ([#20](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/20))

**Full changelog**: [v0.2.4...v0.3.0](https://github.com/sphinx-extensions2/sphinx-subfigure/compare/v0.2.4...v0.3.0)

## v0.2.4 - 2022-09-28

- 🐛 FIX: area labelling for MyST images

## v0.2.3 - 2022-09-28

- 👌 IMPROVE: allow MyST images with no newline

## v0.2.2 - 2022-07-02

- ✨ NEW: add `gap` option ([#8](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/8))

## v0.2.1 - 2022-07-01

- 👌 IMPROVE: allow for myst-parser images

## v0.2.0 - 2022-07-01

- ✨ NEW: support the LaTeX builder ([#5](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/5))
- 👌 IMPROVE: centralise CSS class → `grid-template-areas` ([#4](https://github.com/sphinx-extensions2/sphinx-subfigure/pull/4))
