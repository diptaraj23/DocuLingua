"""PDF rendering helpers using PyMuPDF."""

from __future__ import annotations

import re
from pathlib import Path

from app.learning.content_schema import LearningGuide


def build_learning_guide_pdf(guide: LearningGuide, output_path: str | Path) -> Path:
    """Render a LearningGuide object to a static PDF file."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    _write_pymupdf_pdf(output, guide)
    return output


def render_learning_guide_pdf(guide: LearningGuide, output_path: str | Path) -> Path:
    """Backward-compatible alias for building a learning guide PDF."""

    return build_learning_guide_pdf(guide, output_path)


def _write_pymupdf_pdf(output_path: Path, guide: LearningGuide) -> None:
    """Write a workbook-style PDF with PyMuPDF."""

    try:
        import fitz
    except ImportError as error:
        raise RuntimeError("Could not build PDF because PyMuPDF is unavailable.") from error

    document = fitz.open()
    writer = _FallbackPdfWriter(document)

    sections = [
        "Document Context Overview",
        "Key Vocabulary",
        "Topic-Based Vocabulary Groups",
        "Important Verbs",
        "Grammar Patterns",
        "Useful Phrases and Expressions",
        "Mini Language Lessons",
        "Practice Exercises",
        "Short Reading Practice",
        "Review Sheet",
        "Answer Key",
        "Generation Information",
    ]

    writer.cover_page(
        guide.title,
        f"{guide.source_language} to {guide.explanation_language}",
        f"Learner level: {guide.learner_level}",
        "A static language-learning workbook generated from the uploaded document context.",
    )
    writer.table_of_contents(sections)

    writer.section("1. Document Context Overview")
    writer.paragraph(guide.overview.summary)
    writer.callout("Estimated Difficulty", [guide.overview.estimated_level, guide.overview.difficulty_notes])
    writer.callout("Learning Goals", guide.overview.main_learning_focus)
    writer.callout("How to Study This Guide", guide.overview.suggested_study_approach)

    stats = guide.overview.learning_statistics
    writer.subheading("Learning Statistics")
    writer.table(
        ["Metric", "Count"],
        [
            ["Vocabulary words", str(stats.vocabulary_count)],
            ["Topic-specific words", str(stats.topic_specific_words)],
            ["Important verbs", str(stats.important_verbs)],
            ["Useful phrases", str(stats.useful_phrases)],
            ["Grammar concepts", str(stats.grammar_concepts)],
            ["Practice exercises", str(stats.practice_exercises)],
            ["Mini lessons", str(stats.mini_lessons)],
        ],
    )

    writer.section("2. Key Vocabulary")
    writer.table(
        ["Term", "Meaning", "Why It Matters"],
        [
            [
                item.term,
                f"{item.translation}" + (f" ({item.part_of_speech})" if item.part_of_speech else ""),
                item.note or item.example_sentence,
            ]
            for item in guide.key_vocabulary
        ],
    )

    writer.section("3. Topic-Based Vocabulary Groups")
    for group in guide.vocabulary_groups:
        writer.subheading(group.topic)
        writer.bullets([f"{item.term}: {item.translation}" for item in group.items])

    writer.section("4. Important Verbs")
    writer.table(
        ["Verb", "Meaning", "Form / Note"],
        [
            [
                verb.infinitive,
                verb.translation,
                "; ".join(part for part in [verb.tense_or_form, verb.example_sentence] if part),
            ]
            for verb in guide.important_verbs
        ],
    )

    writer.section("5. Grammar Patterns")
    for pattern in guide.grammar_patterns:
        writer.subheading(pattern.name)
        writer.paragraph(pattern.explanation)
        writer.bullets(pattern.examples)

    writer.section("6. Useful Phrases and Expressions")
    for phrase in guide.useful_phrases:
        writer.card(phrase.phrase, [phrase.translation, phrase.usage_note])

    writer.section("7. Mini Language Lessons")
    for lesson in guide.mini_lessons:
        writer.subheading(lesson.title)
        writer.paragraph(lesson.explanation)
        writer.bullets(lesson.examples)
        if lesson.practice_tip:
            writer.callout("Practice Tip", [lesson.practice_tip])

    writer.section("8. Practice Exercises")
    for exercise in guide.practice_exercises:
        writer.subheading(exercise.title)
        writer.paragraph(exercise.instructions)
        writer.numbered(_clean_numbered_items(exercise.questions))

    writer.section("9. Short Reading Practice")
    writer.paragraph(guide.reading_practice.passage)
    writer.subheading("Questions")
    writer.numbered(guide.reading_practice.questions)

    writer.section("10. Review Sheet")
    writer.subheading("Key Points")
    writer.bullets(guide.review_sheet.key_points)
    writer.subheading("Vocabulary to Review")
    writer.paragraph(", ".join(guide.review_sheet.vocabulary_to_review))
    writer.subheading("Grammar to Review")
    writer.paragraph(", ".join(guide.review_sheet.grammar_to_review))
    writer.subheading("Study Plan")
    writer.numbered(guide.review_sheet.study_plan)

    writer.section("11. Answer Key")
    writer.numbered(_clean_numbered_items(guide.answer_key))

    if guide.generation_metadata and guide.generation_metadata.sections:
        writer.section("Generation Information")
        writer.table(
            ["Section", "Provider", "Model", "Status"],
            [
                [
                    row["section_name"],
                    row["provider"],
                    row["model"],
                    row["status"],
                ]
                for row in guide.generation_metadata.to_display_rows()
            ],
            compact=True,
        )

    document.save(output_path)
    document.close()


def _write_pymupdf_fallback_pdf(output_path: Path, guide: LearningGuide) -> None:
    """Backward-compatible alias for the PyMuPDF PDF writer."""

    _write_pymupdf_pdf(output_path, guide)


class _FallbackPdfWriter:
    """Small workbook-layout helper for the PyMuPDF fallback PDF."""

    def __init__(self, document) -> None:
        self.document = document
        self.page = None
        self.y = 0.0
        self.margin = 54.0
        self.width = 595.0
        self.height = 842.0
        self.bottom = 790.0
        self.accent = (0.06, 0.28, 0.30)
        self.muted = (0.40, 0.45, 0.46)
        self.body = (0.13, 0.15, 0.16)
        self._new_page()

    def cover_page(self, title: str, subtitle: str, level: str, note: str) -> None:
        """Write a distinct cover page."""

        self.y = 120
        self._rule(height=3, color=self.accent)
        self._write(title, size=26, color=self.accent, spacing_after=14)
        self._write(subtitle, size=15, color=self.body, spacing_after=8)
        self._write(level, size=13, color=self.muted, spacing_after=28)
        self.box("About This Guide", [note, "Use the sections in order: overview, vocabulary, grammar, practice, review."])
        self._new_page()

    def table_of_contents(self, sections: list[str]) -> None:
        """Write a simple table of contents."""

        self.section("Table of Contents", new_page=False)
        for index, section in enumerate(sections, start=1):
            if section == "Generation Information":
                label = section
            else:
                label = f"{index}. {section}"
            self._write(label, size=11, indent=8, spacing_after=5)
        self._new_page()

    def section(self, text: str, new_page: bool = True) -> None:
        """Write a major workbook section heading."""

        if new_page and self.y > self.margin + 20:
            self._new_page()
        self._rule(height=1.5, color=self.accent)
        self._write(text, size=17, color=self.accent, spacing_after=12)

    def subheading(self, text: str) -> None:
        """Write a subsection heading."""

        self._write(text, size=12.5, color=self.accent, spacing_after=6)

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

    def callout(self, title: str, items: list[str]) -> None:
        """Write a small highlighted learning callout."""

        cleaned = [item for item in items if item]
        if not cleaned:
            return
        self.box(title, cleaned)

    def card(self, title: str, lines: list[str]) -> None:
        """Write a compact phrase or lesson card."""

        self.box(title, [line for line in lines if line])

    def box(self, title: str, lines: list[str]) -> None:
        """Write a bordered text box."""

        clean_lines = [line for line in lines if line]
        if not title and not clean_lines:
            return
        start_y = self.y
        estimated_lines = 1 + sum(max(1, len(str(line)) // 72 + 1) for line in clean_lines)
        height = max(42, estimated_lines * 13 + 22)
        if self.y + height > self.bottom:
            self._new_page()
            start_y = self.y
        rect = (self.margin - 4, start_y - 4, self.width - self.margin + 4, start_y + height)
        self.page.draw_rect(rect, color=(0.78, 0.84, 0.84), fill=(0.96, 0.98, 0.98), width=0.6)
        self._write(title, size=11.5, color=self.accent, indent=4, spacing_after=4)
        for line in clean_lines:
            self._write(line, size=9.8, indent=8, spacing_after=3)
        self.y = max(self.y, start_y + height + 8)

    def table(self, headers: list[str], rows: list[list[str]], compact: bool = False) -> None:
        """Write a simple wrapped table."""

        if not rows:
            return
        widths = _column_widths(len(headers), self.width - (2 * self.margin))
        self._table_row(headers, widths, header=True, compact=compact)
        for row in rows:
            values = [str(value) for value in row]
            self._table_row(values, widths, compact=compact)
        self.y += 8

    def _table_row(
        self,
        cells: list[str],
        widths: list[float],
        header: bool = False,
        compact: bool = False,
    ) -> None:
        size = 8.2 if compact else 9.2
        line_height = size * 1.25
        wrapped = []
        for cell, width in zip(cells, widths):
            max_chars = max(10, int(width / (size * 0.48)))
            wrapped.append(_wrap_text(_normalize_pdf_text(cell), max_chars))
        row_lines = max(len(lines) for lines in wrapped)
        row_height = row_lines * line_height + 8
        if self.y + row_height > self.bottom:
            self._new_page()

        x = self.margin
        fill = (0.91, 0.95, 0.95) if header else None
        for width in widths:
            rect = (x, self.y, x + width, self.y + row_height)
            self.page.draw_rect(rect, color=(0.76, 0.80, 0.80), fill=fill, width=0.4)
            x += width

        x = self.margin
        for lines, width in zip(wrapped, widths):
            y = self.y + 6
            for line in lines:
                self.page.insert_text(
                    (x + 4, y),
                    line,
                    fontsize=size,
                    fontname="helv",
                    color=self.accent if header else self.body,
                )
                y += line_height
            x += width
        self.y += row_height

    def _new_page(self) -> None:
        self.page = self.document.new_page(width=self.width, height=self.height)
        self.y = self.margin

    def _rule(self, height: float = 1.0, color: tuple[float, float, float] | None = None) -> None:
        """Draw a horizontal accent rule."""

        rect = (self.margin, self.y, self.width - self.margin, self.y + height)
        self.page.draw_rect(rect, color=color or self.accent, fill=color or self.accent)
        self.y += height + 14

    def _write(
        self,
        text: str,
        size: float,
        color: tuple[float, float, float] = (0.12, 0.13, 0.14),
        indent: float = 0.0,
        spacing_after: float = 6.0,
        bold: bool = False,
    ) -> None:
        clean_text = _normalize_pdf_text(" ".join(str(text).split()))
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
        self.y += spacing_after


def _normalize_pdf_text(text: str) -> str:
    """Normalize punctuation that basic PDF fonts often render poorly."""

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
        "\u2022": "-",
        "\u00b7": "-",
    }
    normalized = str(text)
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return normalized


def _clean_numbered_items(items: list[str]) -> list[str]:
    """Remove pre-existing numbering before the fallback renderer numbers items."""

    cleaned: list[str] = []
    for item in items:
        text = re.sub(r"^\s*\d+\.\s*", "", str(item)).strip()
        if text:
            cleaned.append(text)
    return cleaned


def _column_widths(column_count: int, total_width: float) -> list[float]:
    """Return readable table widths for the fallback PDF."""

    if column_count == 2:
        return [total_width * 0.38, total_width * 0.62]
    if column_count == 3:
        return [total_width * 0.25, total_width * 0.30, total_width * 0.45]
    if column_count == 4:
        return [total_width * 0.34, total_width * 0.18, total_width * 0.30, total_width * 0.18]
    return [total_width / max(1, column_count)] * column_count


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
