"""Tests for the ``subfigure`` directive, across builders."""

import base64
import re
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from sphinx_pytest.plugin import CreateDoctree

IMAGE_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAHQAAAB0CAYAAABUmhYnAAAEd0lEQVR4Xu2c0ZLjIAwEk///6GzVvZlspWtWksNRnVcwiGmNwHaS5+v1ej38HKPAU6DHsPy3EIGexVOgh/EUqEBPU+Cw9biHCvQwBQ5bjg4V6GEKHLYcHSrQwxQ4bDk6VKCHKXDYcnSoQA9T4LDllB36fD5vlWR9fUvz0+ve9fp0/O7FU7w0n0CXhBSoDiXTRO06FBKKBLLkLvlGgkTp+UvndPzu/ul46Xq7x2/fQ8kR0wtOBaL+1J6uZ+3fPb5Aw0PRtxOWEkigAr3mCJUMuk9cM45uG3ZvJwel8dN4byW8+r1cgWYPVgRaLIlpwqWCT1cgHbr8skOgYUqkgtHwVYfQKZTiTW8rdCgQFWjtt2Pjty3TGdztOB0aHlosuVcHpglJ+h3nUFow7bE6dDOHCjRN2fBty917qEAF+jEHaI+bTlhK0Nsf/aUBpXtYdXy6noDS9dTePf74oYgWRO3dC6b57k6o7vUJFAh3Cz6dMAIV6FWB9FCQlry1f/ejQXLgt9eX6tXu0DSAtL9APysm0OYHI2mCUgVKxxOoQNOcubc/7XnF5yj3LuYPs5Ud+oc5Ry8R6GEpK1CBjlaMuwcvl1xyBC2I8im9T0xva6pPbtL1V+MjPQW6KEQJRAlAggs0vK2oCibQ4g9+LbnXb96THlQBvl5y0yclqYNQAKgAVGIJQHWPpfjf4uv+bUsagECvClCCkL46VIdecyQtKZRhlKGW3OG3LekeQ0DSBOk+1VLCdbdTAqfzlUuuQFPJe/fM9kORQAV6UYBKJslF11NJS0s8xZO2U3zpeO0lNw2g2+HV8dLbKJov1aMKWKDFfyITKKRsegqmjE7H06FpTRHoRwUoQUnu9pJLh4z0EFMdjwRI46ESWwVC8VK7QMN/TRHookDqCB1Knry261AdmmXMdG86xabzd49H83fP1+5QWkB3e7sg4eu06nra46++4K4uqHp9uyACrSKpXS/Q5kMRnUJruN6vnr7Po/VMn9KrepX3UBKgGmD1UVw6P61HoKmi0F+HfhZIhy766NDhU2F66CEgzQXjQRUjjb8aX7tDaYFpwKkgAi0SSAUXaO0Pjkk/HUoKFQ9p0wm/hjcONC2B6W3B24KKv1ZLx0vzgfQoFsyHQJe3LQINHUEZrUNre6wO1aHLw+AvO5QOHdReLbE0/vSeedyhKBWUDh00XpoAAg2/EkIAqD0FlPYXqEDp3Pix/b8/FKUOIMem7fR6j8Yr0fvlYoEWK4JAw0dplOE6dLnrqH5JrCp4NcMFejPQ6h7RnTAUT/eTKkpYiidtH99D04C6bwvS+QX65W8sUMkVaKgAlcRwuLfuNL5Ah/fQKkC6Pi2JKXB6NEjxUTslKF1P7e17KE1YbRfoZwUFuuijQ4v/l5s6VocOOzQFYv9ZBcoldzY8R08VEGiq2Ob9Bbo5oDQ8gaaKbd5foJsDSsMTaKrY5v0FujmgNDyBpopt3l+gmwNKwxNoqtjm/QW6OaA0PIGmim3eX6CbA0rDE2iq2Ob9Bbo5oDS8H8eCMw7yCzx+AAAAAElFTkSuQmCC"
)

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


@pytest.mark.param_file(FIXTURE_PATH / "posttransform_html.txt")
def test_posttransform_html(file_params, sphinx_doctree: CreateDoctree):
    """Test AST output after post-transforms, when using the HTML builder."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "html"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(file_params.content)
    assert not result.warnings
    file_params.assert_expected(result.get_resolved_pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "build_html.txt")
def test_build_html(file_params, sphinx_doctree: CreateDoctree):
    """Test HTML build output."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "html"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(file_params.content)
    assert not result.warnings
    html = BeautifulSoup(
        Path(result.builder.outdir).joinpath("index.html").read_text(), "html.parser"
    )
    fig_html = str(html.select_one("figure.sphinx-subfigure"))
    file_params.assert_expected(fig_html, rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "posttransform_latex.txt")
def test_posttransform_latex(file_params, sphinx_doctree: CreateDoctree):
    """Test AST output after post-transforms, when using the LaTeX builder."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "latex"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(file_params.content)
    assert not result.warnings
    file_params.assert_expected(result.get_resolved_pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "build_latex.txt")
def test_build_latex(file_params, sphinx_doctree: CreateDoctree):
    """Test LaTeX build output."""
    # pin the project name, since the .tex file is named after it
    # and the default project name differs between sphinx versions
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"], "project": "test"})
    sphinx_doctree.buildername = "latex"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(file_params.content)
    assert not result.warnings
    tex = Path(result.builder.outdir).joinpath("test.tex").read_text()
    fig_tex = re.findall(r"\\begin\{figure\}.*\\end\{figure\}", tex, re.DOTALL)[0]
    file_params.assert_expected(fig_tex, rstrip_lines=True)


def test_too_many_images(sphinx_doctree: CreateDoctree):
    """Test that exceeding the maximum number of images errors gracefully."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "html"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    images = "\n\n".join("   .. image:: image.png" for _ in range(27))
    result = sphinx_doctree(f".. subfigure:: 1\n\n{images}\n")
    assert "maximum of 26 images exceeded" in result.warnings


@pytest.mark.parametrize(
    "content,message",
    [
        pytest.param(
            ".. subfigure:: 0\n\n   .. image:: image.png\n",
            "number of columns must be positive",
            id="zero columns",
        ),
        pytest.param(
            ".. subfigure::\n\n   Just a caption\n",
            "no images found",
            id="no images",
        ),
    ],
)
def test_invalid_content(sphinx_doctree: CreateDoctree, content: str, message: str):
    """Test that invalid content produces a clear directive error, not a crash."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "html"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(content)
    assert message in result.warnings


def test_comments_ignored(sphinx_doctree: CreateDoctree):
    """Test that comments in the directive content are ignored."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "html"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(
        ".. subfigure:: A\n\n   .. a comment\n\n   .. image:: image.png\n"
    )
    assert not result.warnings
    assert "comment" not in result.get_resolved_pformat()


def test_gap_unitless(sphinx_doctree: CreateDoctree):
    """Test that unitless gap values default to px (unitless is invalid CSS)."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "html"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(
        ".. subfigure:: AB\n   :gap: 5\n\n"
        "   .. image:: image.png\n\n"
        "   .. image:: image.png\n"
    )
    assert not result.warnings
    html = Path(result.builder.outdir).joinpath("index.html").read_text()
    assert "gap: 5px;" in html


def test_css_breakpoint_order(sphinx_doctree: CreateDoctree):
    """Test that media-query blocks are emitted in ascending breakpoint order,
    regardless of the order in which figures define them (else, with equal
    specificity, a narrower min-width rule would override a wider one)."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "html"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(
        ".. subfigure:: AB\n   :layout-xl: A|B\n\n"
        "   .. image:: image.png\n\n"
        "   .. image:: image.png\n\n"
        ".. subfigure:: AB\n   :layout-lg: A|B\n   :layout-xl: AB\n\n"
        "   .. image:: image.png\n\n"
        "   .. image:: image.png\n"
    )
    assert not result.warnings
    html = Path(result.builder.outdir).joinpath("index.html").read_text()
    assert html.index("min-width: 992px") < html.index("min-width: 1200px")


def test_myst_image_paragraph_trailing_text(sphinx_doctree: CreateDoctree):
    """Test that non-whitespace inline content in a MyST image paragraph
    errors, rather than being silently discarded."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure", "myst_parser"]})
    sphinx_doctree.buildername = "html"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(
        "```{subfigure} A\n![a](image.png) trailing text\n```\n",
        filename="index.md",
    )
    assert "non-image content within an image paragraph" in result.warnings


@pytest.mark.param_file(FIXTURE_PATH / "posttransform_man.txt")
def test_posttransform_man(file_params, sphinx_doctree: CreateDoctree):
    """Test AST output after post-transforms, when using the Man builder."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "man"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(file_params.content)
    assert not result.warnings
    file_params.assert_expected(result.get_resolved_pformat(), rstrip_lines=True)


@pytest.mark.param_file(FIXTURE_PATH / "build_html.txt")
def test_build_man(file_params, sphinx_doctree: CreateDoctree):
    """Test Man build."""
    sphinx_doctree.set_conf({"extensions": ["sphinx_subfigure"]})
    sphinx_doctree.buildername = "man"
    sphinx_doctree.srcdir.joinpath("image.png").write_bytes(IMAGE_PNG)
    result = sphinx_doctree(file_params.content)
    assert not result.warnings
