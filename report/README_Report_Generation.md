# Report Generation README

## Generated Files

- `Project_Report.md` - concise main university report.
- `Project_Report.pdf` - generated PDF version of the main report, if available.
- `diagrams/use_case_diagram.mmd` - Mermaid use case diagram.
- `diagrams/class_or_module_diagram.mmd` - Mermaid class/module diagram.
- `diagrams/sequence_diagram.mmd` - Mermaid sequence diagram.
- `diagrams/architecture_diagram.mmd` - Mermaid architecture diagram.
- `diagrams/database_or_storage_not_applicable.md` - database/storage note.
- `annexes/Annex_A_Diagrams.md` - diagram explanations.
- `annexes/Annex_B_Screenshots.md` - screenshot placeholders.
- `annexes/Annex_C_Demo.md` - demo link placeholder and suggested demo script.
- `annexes/Annex_D_Technical_Notes.md` - setup notes, limitations, and future improvements.

## How to Open the Report

Open `Project_Report.md` in a Markdown viewer, editor, or GitHub. The annexes are separate Markdown files under `annexes/`.

## How to Export Markdown to PDF

If Pandoc is installed:

```bash
pandoc Project_Report.md -o Project_Report.pdf
```

If Pandoc is not installed, open `Project_Report.md` in a Markdown editor such as VS Code and use a Markdown PDF export extension.

## How to Render Mermaid Diagrams

Install Mermaid CLI if needed:

```bash
npm install -g @mermaid-js/mermaid-cli
```

Render a diagram:

```bash
npx @mermaid-js/mermaid-cli -i diagrams/architecture_diagram.mmd -o diagrams/architecture_diagram.png
```

Repeat the command for the other `.mmd` files.

## Manual Steps Still Needed

- Add the demo video or GIF link.
- Add screenshots to Annex B.
- Optionally render Mermaid diagrams to PNG or SVG for submission.
- Verify API keys and selected model names before a live demo.
- If WeasyPrint is required for the demo machine, install its native dependencies following the official WeasyPrint installation guide.
