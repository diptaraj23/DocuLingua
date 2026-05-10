"""PDF rendering helpers using Jinja2 and WeasyPrint."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.learning.content_schema import LearningGuide


TEMPLATE_DIR = Path(__file__).parent / "templates"
STYLE_PATH = Path(__file__).parent / "styles" / "pdf.css"


def render_learning_guide_html(guide: LearningGuide) -> str:
    """Render a LearningGuide object to an HTML string."""

    try:
        environment = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(["html", "xml"]),
        )
        template = environment.get_template("learning_guide.html")
        css = STYLE_PATH.read_text(encoding="utf-8")
        return template.render(guide=guide, css=css)
    except Exception as error:
        raise RuntimeError(f"Could not render learning guide HTML: {error}") from error


def build_learning_guide_pdf(guide: LearningGuide, output_path: str | Path) -> Path:
    """Render a LearningGuide object to a static PDF file."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    html = render_learning_guide_html(guide)

    try:
        from weasyprint import HTML

        HTML(string=html, base_url=str(TEMPLATE_DIR)).write_pdf(output)
    except OSError:
        _write_minimal_pdf(output, guide)
    except Exception as error:
        raise RuntimeError(f"Could not build learning guide PDF: {error}") from error
    return output


def render_learning_guide_pdf(guide: LearningGuide, output_path: str | Path) -> Path:
    """Backward-compatible alias for building a learning guide PDF."""

    return build_learning_guide_pdf(guide, output_path)


def _write_minimal_pdf(output_path: Path, guide: LearningGuide) -> None:
    """Write a tiny fallback PDF when WeasyPrint native libraries are unavailable."""

    lines = [
        guide.title,
        "Document Context Overview",
        guide.overview.summary,
        "Key Vocabulary: " + ", ".join(item.term for item in guide.key_vocabulary),
        "Grammar Patterns: " + ", ".join(item.name for item in guide.grammar_patterns),
        "Mini Language Lessons: " + ", ".join(item.title for item in guide.mini_lessons),
        "Practice Exercises: " + ", ".join(item.title for item in guide.practice_exercises),
        "Review Sheet",
        "Answer Key: " + " ".join(guide.answer_key),
    ]
    text_commands = ["BT /F1 12 Tf 72 740 Td"]
    for index, line in enumerate(lines):
        safe_line = _escape_pdf_text(line[:95])
        if index == 0:
            text_commands.append(f"({safe_line}) Tj")
        else:
            text_commands.append(f"0 -24 Td ({safe_line}) Tj")
    text_commands.append("ET")
    content = "\n".join(text_commands)
    objects = [
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        f"5 0 obj << /Length {len(content)} >> stream\n{content}\nendstream endobj\n",
    ]
    pdf = "%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf.encode("latin-1")))
        pdf += obj
    xref_offset = len(pdf.encode("latin-1"))
    pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n"
    pdf += (
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    )
    output_path.write_bytes(pdf.encode("latin-1"))


def _escape_pdf_text(text: str) -> str:
    """Escape text for the simple fallback PDF content stream."""

    encoded = text.encode("latin-1", errors="replace").decode("latin-1")
    return encoded.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
