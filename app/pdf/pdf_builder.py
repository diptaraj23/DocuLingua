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
        _write_pymupdf_fallback_pdf(output, guide)
    except Exception as error:
        raise RuntimeError(f"Could not build learning guide PDF: {error}") from error
    return output


def render_learning_guide_pdf(guide: LearningGuide, output_path: str | Path) -> Path:
    """Backward-compatible alias for building a learning guide PDF."""

    return build_learning_guide_pdf(guide, output_path)


def _write_pymupdf_fallback_pdf(output_path: Path, guide: LearningGuide) -> None:
    """Write a readable PDF fallback when WeasyPrint native libraries are unavailable."""

    try:
        import fitz
    except ImportError as error:
        raise RuntimeError(
            "Could not build PDF because WeasyPrint native libraries are missing and PyMuPDF is unavailable."
        ) from error

    document = fitz.open()
    writer = _FallbackPdfWriter(document)

    writer.heading(guide.title, level=1)
    writer.paragraph(f"{guide.source_language} to {guide.explanation_language} | Level {guide.learner_level}")
    writer.paragraph("Static PDF learning guide generated from the uploaded document context.")

    writer.heading("Document Context Overview")
    writer.paragraph(guide.overview.summary)
    writer.bullets(
        [
            f"Estimated level: {guide.overview.estimated_level}",
            f"Difficulty notes: {guide.overview.difficulty_notes}",
            "Main learning focus: " + "; ".join(guide.overview.main_learning_focus),
            "Suggested approach: " + "; ".join(guide.overview.suggested_study_approach),
        ]
    )

    stats = guide.overview.learning_statistics
    writer.heading("Learning Statistics")
    writer.bullets(
        [
            f"Vocabulary words: {stats.vocabulary_count}",
            f"Topic-specific words: {stats.topic_specific_words}",
            f"Important verbs: {stats.important_verbs}",
            f"Useful phrases: {stats.useful_phrases}",
            f"Grammar concepts: {stats.grammar_concepts}",
            f"Practice exercises: {stats.practice_exercises}",
            f"Mini lessons: {stats.mini_lessons}",
        ]
    )

    writer.heading("Key Vocabulary")
    for item in guide.key_vocabulary:
        writer.paragraph(
            f"{item.term}: {item.translation}"
            + (f" ({item.part_of_speech})" if item.part_of_speech else "")
            + (f" - {item.note}" if item.note else "")
        )

    writer.heading("Topic-Based Vocabulary Groups")
    for group in guide.vocabulary_groups:
        writer.heading(group.topic, level=3)
        writer.bullets([f"{item.term}: {item.translation}" for item in group.items])

    writer.heading("Important Verbs")
    for verb in guide.important_verbs:
        writer.paragraph(
            f"{verb.infinitive}: {verb.translation}"
            + (f" | Form: {verb.tense_or_form}" if verb.tense_or_form else "")
            + (f" | Example: {verb.example_sentence}" if verb.example_sentence else "")
        )

    writer.heading("Grammar Patterns")
    for pattern in guide.grammar_patterns:
        writer.heading(pattern.name, level=3)
        writer.paragraph(pattern.explanation)
        writer.bullets(pattern.examples)

    writer.heading("Useful Phrases and Expressions")
    for phrase in guide.useful_phrases:
        writer.paragraph(f"{phrase.phrase}: {phrase.translation} - {phrase.usage_note}")

    writer.heading("Mini Language Lessons")
    for lesson in guide.mini_lessons:
        writer.heading(lesson.title, level=3)
        writer.paragraph(lesson.explanation)
        writer.bullets(lesson.examples)
        if lesson.practice_tip:
            writer.paragraph(f"Tip: {lesson.practice_tip}")

    writer.heading("Practice Exercises")
    for exercise in guide.practice_exercises:
        writer.heading(exercise.title, level=3)
        writer.paragraph(exercise.instructions)
        writer.numbered(exercise.questions)

    writer.heading("Short Reading Practice")
    writer.paragraph(guide.reading_practice.passage)
    writer.heading("Questions", level=3)
    writer.numbered(guide.reading_practice.questions)

    writer.heading("Review Sheet")
    writer.heading("Key Points", level=3)
    writer.bullets(guide.review_sheet.key_points)
    writer.heading("Vocabulary to Review", level=3)
    writer.paragraph(", ".join(guide.review_sheet.vocabulary_to_review))
    writer.heading("Grammar to Review", level=3)
    writer.paragraph(", ".join(guide.review_sheet.grammar_to_review))
    writer.heading("Study Plan", level=3)
    writer.numbered(guide.review_sheet.study_plan)

    writer.heading("Answer Key")
    writer.numbered(guide.answer_key + [f"Reading Practice: {answer}" for answer in guide.reading_practice.answers])

    if guide.generation_metadata and guide.generation_metadata.sections:
        writer.heading("Generation Information")
        for row in guide.generation_metadata.to_display_rows():
            writer.paragraph(
                f"{row['section_name']}: {row['status']} | Provider: {row['provider']} | Model: {row['model']}"
            )

    document.save(output_path)
    document.close()


class _FallbackPdfWriter:
    """Small text-layout helper for the PyMuPDF fallback PDF."""

    def __init__(self, document) -> None:
        self.document = document
        self.page = None
        self.y = 0.0
        self.margin = 54.0
        self.width = 595.0
        self.height = 842.0
        self.bottom = 790.0
        self._new_page()

    def heading(self, text: str, level: int = 2) -> None:
        """Write a section heading."""

        size = 22 if level == 1 else 15 if level == 2 else 12
        spacing = 16 if level == 1 else 10
        self._write(text, size=size, color=(0.08, 0.23, 0.23), spacing_after=spacing, bold=True)

    def paragraph(self, text: str) -> None:
        """Write a paragraph."""

        if text:
            self._write(text, size=10.5, spacing_after=7)

    def bullets(self, items: list[str]) -> None:
        """Write bullet list items."""

        for item in items:
            if item:
                self._write(f"- {item}", size=10.2, indent=12, spacing_after=4)
        self.y += 3

    def numbered(self, items: list[str]) -> None:
        """Write numbered list items."""

        for index, item in enumerate(items, start=1):
            if item:
                self._write(f"{index}. {item}", size=10.2, indent=12, spacing_after=4)
        self.y += 3

    def _new_page(self) -> None:
        self.page = self.document.new_page(width=self.width, height=self.height)
        self.y = self.margin

    def _write(
        self,
        text: str,
        size: float,
        color: tuple[float, float, float] = (0.12, 0.13, 0.14),
        indent: float = 0.0,
        spacing_after: float = 6.0,
        bold: bool = False,
    ) -> None:
        clean_text = " ".join(str(text).split())
        if not clean_text:
            return

        line_height = size * 1.35
        max_chars = max(35, int((self.width - (2 * self.margin) - indent) / (size * 0.48)))
        lines = _wrap_text(clean_text, max_chars)
        needed_height = max(line_height, len(lines) * line_height) + spacing_after
        if self.y + needed_height > self.bottom:
            self._new_page()

        fontname = "helv"
        for line in lines:
            self.page.insert_text(
                (self.margin + indent, self.y),
                line,
                fontsize=size,
                fontname=fontname,
                color=color,
            )
            self.y += line_height
        if bold:
            self.y += 2
        self.y += spacing_after


def _wrap_text(text: str, max_chars: int) -> list[str]:
    """Wrap text into simple character-count lines for the fallback PDF."""

    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines
