from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted
)

source = Path("docs/project_report.md")
output = Path("docs/project_report.pdf")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CodeText",
    parent=styles["Code"],
    fontSize=7,
    leading=9,
))
story = []
in_code = False
code_lines = []

for line in source.read_text(encoding="utf-8").splitlines():
    if line.strip().startswith("```"):
        if in_code:
            story.append(Preformatted("\n".join(code_lines), styles["CodeText"]))
            story.append(Spacer(1, 8))
            code_lines = []
        in_code = not in_code
        continue

    if in_code:
        code_lines.append(line)
        continue

    if not line.strip():
        story.append(Spacer(1, 5))
    elif line.startswith("# "):
        story.append(Paragraph(escape(line[2:]), styles["Title"]))
    elif line.startswith("## "):
        story.append(Paragraph(escape(line[3:]), styles["Heading1"]))
    elif line.startswith("### "):
        story.append(Paragraph(escape(line[4:]), styles["Heading2"]))
    elif line.startswith("- ") or line.startswith("* "):
        story.append(Paragraph("• " + escape(line[2:]), styles["BodyText"]))
    else:
        story.append(Paragraph(escape(line), styles["BodyText"]))

doc = SimpleDocTemplate(
    str(output),
    pagesize=(8.5 * inch, 11 * inch),
    rightMargin=0.65 * inch,
    leftMargin=0.65 * inch,
    topMargin=0.65 * inch,
    bottomMargin=0.65 * inch,
)

doc.build(story)
print("PDF created:", output)