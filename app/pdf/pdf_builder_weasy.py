"""PDF rendering helpers using WeasyPrint."""

from __future__ import annotations

import html
import re
from pathlib import Path

from app.learning.content_schema import LearningGuide


def _write_weasyprint_pdf(output_path: Path, guide: LearningGuide) -> None:
    try:
        from weasyprint import HTML, CSS
    except ImportError as error:
        raise RuntimeError("Could not build PDF because WeasyPrint is unavailable.") from error

    html_content = _render_learning_guide_html(guide)
    css_content = _default_pdf_css()

    HTML(string=html_content).write_pdf(
        output_path,
        stylesheets=[CSS(string=css_content)],
    )


def _render_learning_guide_html(guide: LearningGuide) -> str:
    stats = guide.overview.learning_statistics

    generation_metadata_html = ""
    if guide.generation_metadata and guide.generation_metadata.sections:
        rows = []
        for row in guide.generation_metadata.to_display_rows():
            rows.append(
                _table_row(
                    [
                        row["section_name"],
                        row["provider"],
                        row["model"],
                        row["status"],
                    ]
                )
            )
        generation_metadata_html = f"""
        <section class="page-break">
            <h1>Generation Information</h1>
            {_render_table(
                ["Section", "Provider", "Model", "Status"],
                rows,
                table_class="compact-table"
            )}
        </section>
        """

    vocabulary_rows = [
        _table_row(
            [
                item.term,
                f"{item.translation}" + (f" ({item.part_of_speech})" if item.part_of_speech else ""),
                item.note or item.example_sentence,
            ]
        )
        for item in guide.key_vocabulary
    ]

    verb_rows = [
        _table_row(
            [
                verb.infinitive,
                verb.translation,
                "; ".join(part for part in [verb.tense_or_form, verb.example_sentence] if part),
            ]
        )
        for verb in guide.important_verbs
    ]

    vocabulary_groups_html = "".join(
        f"""
        <div class="group-block">
            <h2>{_escape(group.topic)}</h2>
            {_render_bullets([f"{item.term}: {item.translation}" for item in group.items])}
        </div>
        """
        for group in guide.vocabulary_groups
    )

    grammar_html = "".join(
        f"""
        <div class="content-block">
            <h2>{_escape(pattern.name)}</h2>
            <p>{_escape(pattern.explanation)}</p>
            {_render_bullets(pattern.examples)}
        </div>
        """
        for pattern in guide.grammar_patterns
    )

    phrases_html = "".join(
        f"""
        <div class="card">
            <h3>{_escape(phrase.phrase)}</h3>
            <p>{_escape(phrase.translation)}</p>
            <p>{_escape(phrase.usage_note)}</p>
        </div>
        """
        for phrase in guide.useful_phrases
    )

    lessons_html = "".join(
        f"""
        <div class="content-block">
            <h2>{_escape(lesson.title)}</h2>
            <p>{_escape(lesson.explanation)}</p>
            {_render_bullets(lesson.examples)}
            {_render_callout("Practice Tip", [lesson.practice_tip]) if lesson.practice_tip else ""}
        </div>
        """
        for lesson in guide.mini_lessons
    )

    exercises_html = "".join(
        f"""
        <div class="content-block">
            <h2>{_escape(exercise.title)}</h2>
            <p>{_escape(exercise.instructions)}</p>
            {_render_numbered(_clean_numbered_items(exercise.questions))}
        </div>
        """
        for exercise in guide.practice_exercises
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{_escape(guide.title)}</title>
    </head>
    <body>
        <section class="cover-page">
            <div class="accent-line"></div>
            <h1 class="cover-title">{_escape(guide.title)}</h1>
            <p class="cover-subtitle">{_escape(guide.source_language)} to {_escape(guide.explanation_language)}</p>
            <p class="cover-level">Learner level: {_escape(guide.learner_level)}</p>

            <div class="callout">
                <h3>About This Guide</h3>
                <p>A static language-learning workbook generated from the uploaded document context.</p>
                <p>Use the sections in order: overview, vocabulary, grammar, practice, review.</p>
            </div>
        </section>

        <section class="page-break">
            <h1>Table of Contents</h1>
            <ol class="toc">
                <li>Document Context Overview</li>
                <li>Key Vocabulary</li>
                <li>Topic-Based Vocabulary Groups</li>
                <li>Important Verbs</li>
                <li>Grammar Patterns</li>
                <li>Useful Phrases and Expressions</li>
                <li>Mini Language Lessons</li>
                <li>Practice Exercises</li>
                <li>Short Reading Practice</li>
                <li>Review Sheet</li>
                <li>Answer Key</li>
                {"<li>Generation Information</li>" if generation_metadata_html else ""}
            </ol>
        </section>

        <section class="page-break">
            <h1>1. Document Context Overview</h1>
            <p>{_escape(guide.overview.summary)}</p>

            {_render_callout("Estimated Difficulty", [guide.overview.estimated_level, guide.overview.difficulty_notes])}
            {_render_callout("Learning Goals", guide.overview.main_learning_focus)}
            {_render_callout("How to Study This Guide", guide.overview.suggested_study_approach)}

            <h2>Learning Statistics</h2>
            {_render_table(
                ["Metric", "Count"],
                [
                    _table_row(["Vocabulary words", str(stats.vocabulary_count)]),
                    _table_row(["Topic-specific words", str(stats.topic_specific_words)]),
                    _table_row(["Important verbs", str(stats.important_verbs)]),
                    _table_row(["Useful phrases", str(stats.useful_phrases)]),
                    _table_row(["Grammar concepts", str(stats.grammar_concepts)]),
                    _table_row(["Practice exercises", str(stats.practice_exercises)]),
                    _table_row(["Mini lessons", str(stats.mini_lessons)]),
                ],
            )}
        </section>

        <section class="page-break">
            <h1>2. Key Vocabulary</h1>
            {_render_table(["Term", "Meaning", "Why It Matters"], vocabulary_rows)}
        </section>

        <section class="page-break">
            <h1>3. Topic-Based Vocabulary Groups</h1>
            {vocabulary_groups_html}
        </section>

        <section class="page-break">
            <h1>4. Important Verbs</h1>
            {_render_table(["Verb", "Meaning", "Form / Note"], verb_rows)}
        </section>

        <section class="page-break">
            <h1>5. Grammar Patterns</h1>
            {grammar_html}
        </section>

        <section class="page-break">
            <h1>6. Useful Phrases and Expressions</h1>
            {phrases_html}
        </section>

        <section class="page-break">
            <h1>7. Mini Language Lessons</h1>
            {lessons_html}
        </section>

        <section class="page-break">
            <h1>8. Practice Exercises</h1>
            {exercises_html}
        </section>

        <section class="page-break">
            <h1>9. Short Reading Practice</h1>
            <p>{_escape(guide.reading_practice.passage)}</p>
            <h2>Questions</h2>
            {_render_numbered(guide.reading_practice.questions)}
        </section>

        <section class="page-break">
            <h1>10. Review Sheet</h1>
            <h2>Key Points</h2>
            {_render_bullets(guide.review_sheet.key_points)}

            <h2>Vocabulary to Review</h2>
            <p>{_escape(", ".join(guide.review_sheet.vocabulary_to_review))}</p>

            <h2>Grammar to Review</h2>
            <p>{_escape(", ".join(guide.review_sheet.grammar_to_review))}</p>

            <h2>Study Plan</h2>
            {_render_numbered(guide.review_sheet.study_plan)}
        </section>

        <section class="page-break">
            <h1>11. Answer Key</h1>
            {_render_numbered(_clean_numbered_items(guide.answer_key))}
        </section>

        {generation_metadata_html}
    </body>
    </html>
    """
    return html_content


def _default_pdf_css() -> str:
    return """
    @page {
        size: A4;
        margin: 18mm 16mm 18mm 16mm;
    }

    body {
        font-family: Arial, sans-serif;
        font-size: 11px;
        line-height: 1.45;
        color: #202426;
    }

    h1, h2, h3 {
        color: #12484d;
        margin-top: 0;
    }

    h1 {
        font-size: 20px;
        margin-bottom: 10px;
        page-break-after: avoid;
    }

    h2 {
        font-size: 14px;
        margin-top: 16px;
        margin-bottom: 6px;
        page-break-after: avoid;
    }

    h3 {
        font-size: 12px;
        margin-top: 10px;
        margin-bottom: 4px;
        page-break-after: avoid;
    }

    p, li {
        orphans: 3;
        widows: 3;
    }

    .cover-page {
        padding-top: 40mm;
    }

    .cover-title {
        font-size: 26px;
        margin-bottom: 10px;
    }

    .cover-subtitle {
        font-size: 15px;
        margin-bottom: 4px;
    }

    .cover-level {
        color: #5c6668;
        margin-bottom: 18px;
    }

    .accent-line {
        height: 4px;
        width: 100%;
        background: #12484d;
        margin-bottom: 20px;
    }

    .callout,
    .card {
        border: 1px solid #c7d6d6;
        background: #f7fbfb;
        padding: 10px 12px;
        margin: 10px 0 14px 0;
        border-radius: 4px;
        page-break-inside: avoid;
    }

    .content-block,
    .group-block {
        margin-bottom: 14px;
        page-break-inside: avoid;
    }

    ul, ol {
        margin: 6px 0 10px 20px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        margin: 10px 0 16px 0;
        font-size: 10px;
    }

    th, td {
        border: 1px solid #c2cccc;
        padding: 7px 8px;
        vertical-align: top;
        word-wrap: break-word;
        overflow-wrap: anywhere;
    }

    th {
        background: #e9f2f2;
        color: #12484d;
        text-align: left;
    }

    thead {
        display: table-header-group;
    }

    tr {
        page-break-inside: avoid;
    }

    .compact-table {
        font-size: 9px;
    }

    .page-break {
        page-break-before: always;
    }

    .toc li {
        margin-bottom: 6px;
    }
    """


def _render_table(headers: list[str], row_html: list[str], table_class: str = "") -> str:
    class_attr = f' class="{table_class}"' if table_class else ""
    header_html = "".join(f"<th>{_escape(header)}</th>" for header in headers)
    body_html = "".join(row_html)
    return f"""
    <table{class_attr}>
        <thead>
            <tr>{header_html}</tr>
        </thead>
        <tbody>
            {body_html}
        </tbody>
    </table>
    """


def _table_row(cells: list[str]) -> str:
    return "<tr>" + "".join(f"<td>{_escape(cell)}</td>" for cell in cells) + "</tr>"


def _render_bullets(items: list[str]) -> str:
    cleaned = [item for item in items if item]
    if not cleaned:
        return "<p>No items available.</p>"
    return "<ul>" + "".join(f"<li>{_escape(item)}</li>" for item in cleaned) + "</ul>"


def _render_numbered(items: list[str]) -> str:
    cleaned = [item for item in items if item]
    if not cleaned:
        return "<p>No items available.</p>"
    return "<ol>" + "".join(f"<li>{_escape(item)}</li>" for item in cleaned) + "</ol>"


def _render_callout(title: str, items: list[str]) -> str:
    cleaned = [item for item in items if item]
    if not cleaned:
        return ""
    body = "".join(f"<p>{_escape(item)}</p>" for item in cleaned)
    return f"""
    <div class="callout">
        <h3>{_escape(title)}</h3>
        {body}
    </div>
    """


def _escape(value: str) -> str:
    return html.escape(str(value or ""))


def _clean_numbered_items(items: list[str]) -> list[str]:
    cleaned: list[str] = []
    for item in items:
        text = re.sub(r"^\\s*\\d+\\.\\s*", "", str(item)).strip()
        if text:
            cleaned.append(text)
    return cleaned