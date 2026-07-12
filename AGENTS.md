# AGENTS.md

This file provides guidance for AI coding agents working on the **sphinx-subfigure** repository.

## Project Overview

sphinx-subfigure is a [Sphinx](https://www.sphinx-doc.org) extension providing a single `subfigure` directive, to create figures containing multiple images:

- A simple, compact string format for describing complex image grid layouts (e.g. `AA|BC`)
- Full HTML support, with responsive layouts for different screen sizes (via CSS `grid-template-areas`)
- LaTeX support for simple layouts (via the [`subcaption`](https://ctan.org/pkg/subcaption) package), with graceful degradation for layouts it cannot express
- Graceful degradation for all other output formats (images render as a plain figure)
- Figure numbering/referencing, and per-image sub-captions sourced from image `alt` text

The package is small (~500 lines of source) — prefer minimal, surgical changes over restructuring.

## Repository Structure

```
pyproject.toml              # flit packaging, project metadata, tool config
tox.ini                     # tox environments (tests, docs)
.pre-commit-config.yaml     # code style hooks
.github/workflows/ci.yml    # GitHub Actions: pytest matrix + coverage
.readthedocs.yml            # Read the Docs build configuration

src/sphinx_subfigure/
├── __init__.py             # __version__ and setup() re-export
├── main.py                 # SubfigureDirective: content parsing, layout generation + validation
├── tr_html.py              # HTML post-transform, grid/item nodes, responsive CSS injection
└── tr_latex.py             # LaTeX post-transform, subfigure environment nodes

tests/
├── test_simple.py          # all tests (pytest-param-files + sphinx-pytest)
└── fixtures/               # file-based test cases (input → expected output)
    ├── posttransform_html.txt   # resolved doctree, HTML builder
    ├── posttransform_latex.txt  # resolved doctree, LaTeX builder
    ├── posttransform_man.txt    # resolved doctree, man builder (fallback behaviour)
    ├── build_html.txt           # rendered HTML of the figure element
    └── build_latex.txt          # rendered LaTeX of the figure environment

docs/
├── conf.py                 # docs configuration (myst-parser + furo theme)
├── index.md                # the entire documentation (single page, MyST Markdown)
└── _static/                # example images A–H and custom.css
```

## Architecture Overview

The extension follows the standard Sphinx directive + post-transform pattern, keeping the
doctree format-agnostic until write time:

```
RST / MyST source
  → SubfigureDirective.run()                       (read phase, main.py)
      - nested-parses directive content
      - each image child is assigned a subfigure_area identifier: "A", "B", "C", ...
      - a paragraph containing only images (as produced by MyST) is unwrapped into images
      - a trailing non-image paragraph becomes the figure caption (max one allowed)
      - layout argument/options are parsed and validated into figure_node["layout"]
        (a dict mapping "default"/"sm"/"lg"/"xl"/"xxl" → list of rows of area names)
      - returns a standard docutils figure node, tagged with is_subfigure
  → format-specific SphinxPostTransform             (priority 199)
      - tr_html.SubfigureHtmlTransform: wraps images in SubfigureGridHtml /
        SubfigureGridItemHtml nodes; records layouts on the document for CSS generation
      - tr_latex.SubfigureLaTexTransform: wraps images in SubfigureEnvLatex nodes,
        but ONLY when the layout is a simple left-to-right/top-to-bottom progression
        of areas; otherwise the figure is left untouched (falls back to a plain figure)
      - other builders: no transform runs; the figure renders as a normal figure
  → writer visitors emit output
      - HTML: inline CSS grid styles on the nodes, plus a per-page <style> block with
        grid-template-areas media queries, injected via the "html-page-context" event
      - LaTeX: \begin{subfigure}{<width>\textwidth} ... \end{subfigure}, with the
        subcaption package added via app.add_latex_package
```

### Layout string format

- An integer `N` produces an N-column grid filled in order (`3` with 4 images → `ABC|D..` padded with `.`)
- Otherwise rows are delimited by `|`; each character is an area name (`A`–`Z`) or `.` for an empty cell
- Validation (per the [CSS grid-template-areas spec](https://www.w3.org/TR/css3-grid-layout/#grid-template-areas-property)):
  all rows must be equal length, every image's area must appear exactly once as a single
  filled-in rectangle, and no undefined areas may be referenced

### Key invariants

- Images are identified positionally: the Nth image in the content is area
  `string.ascii_uppercase[N]` (hence a hard limit of 26 images)
- Sub-captions come from image `alt` attributes when the `subcaptions` option is set
- The LaTeX transform must never crash on layouts it cannot express — it should fall back
  to leaving the figure unmodified (see issue #17 for a historical violation of this)

## Development Commands

### Testing

```bash
# Install with test dependencies
pip install -e ".[testing]"

# Run all tests
pytest

# Run a single test
pytest tests/test_simple.py::test_build_html

# Run with coverage (as CI does)
pytest --cov=sphinx_subfigure --cov-report=term-missing

# Regenerate fixture files after an intentional output change
pytest --regen-file-failure
```

Tests can also be run via `tox`, using a python + sphinx factor env
(e.g. `tox -e py311-sphinx9` — note a bare `tox -e py311` is NOT a
defined env and would run no tests).

### Documentation

```bash
# Build docs from clean (also: BUILDER=linkcheck tox -e docs-clean)
tox -e docs-clean

# Incremental docs build
tox -e docs-update

# Or manually
pip install -e ".[docs]"
sphinx-build -nW --keep-going -b html docs/ docs/_build/html
```

Docs are hosted on Read the Docs, configured by `.readthedocs.yml`, and build with
`fail_on_warning: true` — new pages/options must not introduce warnings.

### Code Quality

```bash
# Run all style checks (required to pass before committing)
pre-commit run --all-files
```

## Testing Guidelines

- All tests live in `tests/test_simple.py` and are parametrized over fixture files via
  [`pytest-param-files`](https://github.com/chrisjsewell/pytest-param-files)
- Fixture files use the format:

  ```
  title of case
  .
  restructuredtext input
  .
  expected output (doctree pformat, HTML, or LaTeX)
  .
  ```

- Sphinx builds are driven by the `sphinx_doctree` fixture from
  [`sphinx-pytest`](https://github.com/chrisjsewell/sphinx-pytest) (`CreateDoctree`),
  which builds a single `index.rst` in a temporary source directory
- `posttransform_*` fixtures assert on the resolved doctree (`get_resolved_pformat()`);
  `build_*` fixtures assert on written output (HTML parsed with BeautifulSoup, LaTeX via regex)
- Every bug fix or new option should add a fixture case for each affected builder,
  including the man/fallback behaviour where relevant
- Fixture output must be stable across all supported Sphinx/docutils versions —
  regenerate with `pytest --regen-file-failure` and check CI across the matrix

## Code Style Guidelines

- Keep `from __future__ import annotations` at the top of modules and use modern
  annotation syntax (`list[str]`, `X | None`)
- Complete type annotations on all function signatures
- Sphinx-style docstrings; short module docstrings on every module
- Style is enforced by pre-commit (see `.pre-commit-config.yaml`), using `ruff-check`
  (with `--fix`) and `ruff-format`; run `pre-commit run --all-files` before committing
- User-facing directive errors should be raised via `self.error(...)` inside the
  directive, with messages prefixed to identify the failing option
  (e.g. `Invalid subfigure layout-sm (...)`)

## Commit Message Format

Use this format (consistent with the repository history and other sphinx-extensions2 /
executablebooks projects):

```
<EMOJI> <KEYWORD>: Summarize in 72 chars or less (#<PR>)

Optional detailed explanation.
```

Keywords:

- `✨ NEW:` – New feature
- `🐛 FIX:` – Bug fix
- `👌 IMPROVE:` – Improvement (no breaking changes)
- `‼️ BREAKING:` – Breaking change
- `📚 DOCS:` – Documentation
- `🔧 MAINTAIN:` – Maintenance changes only (typos, tooling, etc.)
- `🧪 TEST:` – Tests or CI changes only
- `♻️ REFACTOR:` – Refactoring
- `🚀 RELEASE:` – Version release commits (e.g. `🚀 RELEASE: v0.2.4`)

## Pull Request Requirements

1. **Description**: Include a meaningful description explaining the change
2. **Tests**: Include fixture/test cases for new functionality or bug fixes
3. **Documentation**: Update `docs/index.md` (and its options table) if behaviour changes
4. **Code Quality**: Ensure `pre-commit run --all-files` passes

## Key Files

- `src/sphinx_subfigure/main.py` – `SubfigureDirective`, layout parsing and validation;
  the `option_spec` here is the single source of truth for directive options
- `src/sphinx_subfigure/tr_html.py` – HTML nodes/transform and the `html_page_context`
  hook that injects per-page responsive CSS
- `src/sphinx_subfigure/tr_latex.py` – LaTeX nodes/transform (simple-progression layouts only)
- `src/sphinx_subfigure/__init__.py` – `__version__` (flit reads this for packaging;
  bump it for releases) and the `setup()` entry point re-export
- `docs/index.md` – the entire user documentation, including the directive options table

## Reference Documentation

- [Sphinx Extension Development](https://www.sphinx-doc.org/en/master/extdev/index.html)
- [Docutils Documentation](https://docutils.sourceforge.io/)
- [CSS grid-template-areas](https://www.w3.org/TR/css3-grid-layout/#grid-template-areas-property)
- [LaTeX subcaption package](https://ctan.org/pkg/subcaption)
- [MyST-Parser](https://myst-parser.readthedocs.io/) (used for the docs, and its image
  syntax is explicitly supported inside the directive)
