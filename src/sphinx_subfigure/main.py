from __future__ import annotations

import math
import string

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util.docutils import SphinxDirective
from sphinx.writers.html import HTMLTranslator


def setup(app: Sphinx) -> None:
    """Setup the extension."""
    app.add_directive("subfigure", SubfigureDirective)
    app.add_post_transform(SubfigureHtmlTransform)
    app.add_node(
        SubfigureGridHtml, html=(visit_subfigure_grid_html, depart_subfigure_grid_html)
    )
    app.add_node(
        SubfigureGridItemHtml,
        html=(visit_subfigure_grid_item_html, depart_subfigure_grid_item_html),
    )


class SubfigureDirective(SphinxDirective):
    """A sphinx directive to create sub-figures."""

    has_content = True
    required_arguments = 0
    optional_arguments = 1  # the subfigure layout (defaults to 1)
    final_argument_whitespace = True
    option_spec = {
        "layout-sm": directives.unchanged,
        "subcaptions": lambda x: directives.choice(x, ("above", "below")),
        "width": directives.length_or_percentage_or_unitless,
        "align": lambda x: directives.choice(x, ("left", "center", "right")),
        "name": directives.unchanged,
        "class": directives.class_option,
        "class-grid": directives.class_option,
        "class-item": directives.class_option,
    }

    def run(self) -> list[nodes.Element]:
        """Run the directive."""
        self.assert_has_content()
        figure_node = nodes.figure(
            is_subfigure=True,
            classes=["sphinx-subfigure"] + self.options.get("class", []),
            grid_classes=self.options.get("class-grid", []),
            item_classes=self.options.get("class-item", []),
        )
        self.set_source_info(figure_node)
        if self.options.get("align") is not None:
            figure_node["align"] = self.options.get("align")
        if self.options.get("width") is not None:
            figure_node["width"] = self.options.get("width")
        figure_node["subcaptions"] = self.options.get("subcaptions")
        self.add_name(figure_node)
        self.state.nested_parse(self.content, self.content_offset, figure_node)

        number_of_images = 0
        has_caption = False
        for idx, child in enumerate(figure_node):
            if isinstance(child, nodes.image):
                number_of_images += 1
                child["subfigure_area"] = string.ascii_uppercase[idx]
            elif isinstance(child, nodes.paragraph):
                if has_caption:
                    raise self.error("Invalid subfigure layout (multiple captions)")
                child.replace_self(nodes.caption(child.rawsource, *child.children))
            else:
                raise self.error(
                    "subfigure must contain only images and single caption, "
                    f"item {idx + 1} is neither (line {child.line})"
                )

        layout_string = self.arguments[0] if self.arguments else 1
        figure_node["layout"] = self.generate_layout(layout_string, number_of_images)

        if "layout-sm" in self.options:
            figure_node["layout_sm"] = self.generate_layout(
                self.options.get("layout-sm") or 1, number_of_images, "layout-sm"
            )

        return [figure_node]

    def generate_layout(
        self, string: str, items: int, ltype: str = "layout", validate: bool = True
    ) -> list[list[str]]:
        """Generate a layout from a string."""
        layout = self._generate_layout(string, items)
        if validate:
            self._validate_layout(layout, items, ltype)
        return layout

    def _validate_layout(
        self, layout: list[list[str]], items: int, ltype="layout"
    ) -> None:
        """Validate a layout.

        Validated according to https://www.w3.org/TR/css3-grid-layout/#grid-template-areas-property:
        - All areas must be named A-Z.
        - All areas must form a single filled-in rectangle
        """

        prefix = f"Invalid subfigure {ltype}"

        area_indices: dict[str, list[tuple[int, int]]] = {}

        # check all rows have the same number of columns, and retrieve indices of each area
        if not layout:
            raise self.error(f"{prefix} (empty)")
        for rid, row in enumerate(layout):
            if not row:
                raise self.error(f"{prefix} (empty row)")
            if len(row) != len(layout[0]):
                raise self.error(f"{prefix} (row length mismatch)")
            for cid, area in enumerate(row):
                if area != ".":
                    area_indices.setdefault(area, set()).add((rid, cid))

        available_areas = {string.ascii_uppercase[i] for i in range(items)}
        used_areas = set(area_indices)

        # check all areas are used in the layout
        missing_areas = available_areas - used_areas
        if missing_areas:
            raise self.error(f"{prefix} (missing areas {missing_areas})")

        # check all areas correspond to an item
        additional_areas = used_areas - available_areas
        if additional_areas:
            raise self.error(f"{prefix} (invalid areas {additional_areas})")

        # Check that all area_indices form single filled-in rectangles
        for area, indices in area_indices.items():
            if len(indices) == 1:
                continue
            x0, y0 = min(x for x, _ in indices), min(y for _, y in indices)
            x1, y1 = max(x for x, _ in indices), max(y for _, y in indices)
            expected_indices = {
                (x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
            }
            if expected_indices != indices:
                raise self.error(f"{prefix} (area {area} is not a single rectangular)")

    def _generate_layout(self, layout_string: str, items: int) -> list[list[str]]:
        """Generate a figure layout from a string."""
        layout = []

        # if an integer is given, generate a layout with this many columns
        # this is similar to the CSS: grid-template-columns: repeat(columns, 1fr)
        try:
            layout_columns = int(layout_string)
        except ValueError:
            pass
        else:
            for row in range(math.ceil(items / layout_columns)):
                layout.append([])
                for col in range(layout_columns):
                    if (row * layout_columns) + col > items - 1:
                        area = "."
                    else:
                        area = string.ascii_uppercase[(row * layout_columns) + col]
                    layout[row].append(area)
            return layout

        # if a string is given, parse it as a grid layout, with columns delimited by "|",
        # ignore spaces, named areas A-Z and empty areas are filled with "."
        for row_string in layout_string.split("|"):
            row = []
            for col in row_string:
                if not col:
                    continue  # ignore spaces
                row.append(col)
            layout.append(row)
        return layout


class SubfigureGridHtml(nodes.General, nodes.Element):
    """Node for subfigure grid, added only for Html."""


def visit_subfigure_grid_html(self: HTMLTranslator, node: SubfigureGridHtml) -> None:
    """Visit subfigure grid node."""
    classes = " ".join(node["classes"])
    layout = " ".join(["'" + " ".join(row) + "'" for row in node["layout"]])
    if node.get("layout_sm"):
        layout_default_class = "layout-default-" + "_".join(
            ["".join(row) for row in node["layout"]]
        )
        layout_sm = " ".join(["'" + " ".join(row) + "'" for row in node["layout_sm"]])
        layout_sm_class = "layout-sm-" + "_".join(
            ["".join(row) for row in node["layout_sm"]]
        )
        classes += " " + layout_default_class + " " + layout_sm_class
        # TODO deduplicate-this? make width configurable?
        self.body.append(
            "<style>\n"
            f"div.{layout_default_class} {{\n"
            f"  grid-template-areas: {layout};\n"
            "}\n"
            "@media (max-width: 576px) {\n"
            f"  div.{layout_sm_class} {{\n"
            f"    grid-template-areas: {layout_sm};\n"
            "  }\n"
            "}\n"
            "</style>\n"
        )
        self.body.append(f'<div class="{classes}" style="display: grid;">\n')
    else:
        self.body.append(
            f'<div class="{classes}" style="display: grid; grid-template-areas: {layout};">\n'
        )


def depart_subfigure_grid_html(self: HTMLTranslator, node: SubfigureGridHtml) -> None:
    """Depart subfigure grid node."""
    self.body.append("</div>\n")


class SubfigureGridItemHtml(nodes.General, nodes.Element):
    """Node for subfigure grid item, added only for Html."""


def visit_subfigure_grid_item_html(
    self: HTMLTranslator, node: SubfigureGridItemHtml
) -> None:
    """Visit subfigure grid item node."""
    classes = " ".join(node["classes"])
    style = "display: flex; flex-direction: column; justify-content: center; align-items: center;"
    style += f" grid-area: {node['area']};"
    self.body.append(f'<div class="{classes}" style="{style}">\n')
    if "caption" in node and node["caption-align"] == "above":
        self.body.append(f'<span class="caption">{node["caption"]}</span>\n')


def depart_subfigure_grid_item_html(
    self: HTMLTranslator, node: SubfigureGridItemHtml
) -> None:
    """Depart subfigure grid item node."""
    if "caption" in node and node["caption-align"] == "below":
        self.body.append(f'<span class="caption">{node["caption"]}</span>\n')
    self.body.append("</div>\n")


class SubfigureHtmlTransform(SphinxPostTransform):
    """Transform subfigure containers into the HTML specific AST structures."""

    default_priority = 199
    formats = ("html",)

    def run(self) -> None:
        """Run the transform."""

        # docutils <0.18 (traverse) >=0.18 (findall) compatibility
        for fig_node in _findall(
            self.document, lambda n: "is_subfigure" in getattr(n, "attributes", {})
        ):

            # initiate figure children
            children = []

            # add grid
            grid_node = SubfigureGridHtml(
                layout=fig_node["layout"], classes=fig_node.get("grid_classes", [])
            )
            if "layout_sm" in fig_node:
                grid_node["layout_sm"] = fig_node["layout_sm"]
            children.append(grid_node)

            # add image items to grid
            caption = None
            item_classes = ["sphinx-subfigure-item"] + fig_node.get("item_classes", [])
            for child in fig_node:
                if isinstance(child, nodes.caption):
                    caption = child
                    continue
                item_node = SubfigureGridItemHtml(classes=item_classes)
                # if fig_node["layout_type"] == "areas":
                item_node["area"] = child["subfigure_area"]
                if fig_node["subcaptions"] and child.get("alt"):
                    item_node["caption-align"] = fig_node["subcaptions"]
                    item_node["caption"] = child["alt"]
                item_node.append(child)
                grid_node.append(item_node)

            # add caption
            if caption:
                children.append(caption)

            fig_node.children = children


def _findall(node, *args, **kwargs):
    """Compatibility for docutils <0.18."""
    return getattr(node, "findall", node.traverse)(*args, **kwargs)
