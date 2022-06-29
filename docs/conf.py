project = "Sphinx Subfigures"
author = "Chris Sewell"

extensions = ["myst_parser", "sphinx_subfigure"]

myst_enable_extensions = ["colon_fence"]
numfig = True

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
