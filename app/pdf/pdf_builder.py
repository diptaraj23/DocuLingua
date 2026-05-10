"""PDF rendering helpers using Jinja2 and WeasyPrint."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app.learning.content_schema import LearningGuide


TEMPLATE_DIR = Path(__file__).parent / "templates"
STYLE_PATH = Path(__file__).parent / "styles" / "pdf.css"


def render_learning_guide_pdf(guide: LearningGuide, output_path: str | Path) -> Path:
    """Render a LearningGuide object to a static PDF file."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    environment = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = environment.get_template("learning_guide.html")
    html = template.render(guide=guide, css_path=STYLE_PATH.resolve())

    HTML(string=html, base_url=str(TEMPLATE_DIR)).write_pdf(output)
    return output
