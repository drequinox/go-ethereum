# Reporting (Phase 8)

One source, many renderings. Write the report once as `review/report.md` and render every requested format from it. Never hand-author formats separately.

## Working layout

```
review/
  report.md                     canonical report (pandoc Markdown, images referenced as diagrams/NAME.EXT)
  diagrams/F1.mmd               flow as documented
  diagrams/F1-annotated.mmd     flow with findings and open questions pinned to messages
  diagrams/AT-S1.mmd            attack tree per invariant
  diagrams/cx-*.mmd             counterexample traces copied from the simulation output
  sim/                          F<n>_model.py, sim_out/
  out/                          rendered deliverables
```

## Report sections

1. Title block: system, baseline (document hashes), profiles, mode, date, intelligence refresh date or "not refreshed".
2. Executive summary and verdict: one page, plain language, readable by a non-specialist.
3. Scope, and what was not assured.
4. Documentation gaps.
5. System model: flows as documented, step table, registers, trust assumptions.
6. Intelligence summary: the items that changed the analysis.
7. Invariants, with standard mapping.
8. Question log.
9. Threat model: attack trees, minimal compromise sets, incident pattern check.
10. Simulation: model summary, bounds, counterexamples, empirical compromise sets, before/after for proposed fixes.
11. Traceability matrix.
12. Findings, each beside its annotated or counterexample MSC.
13. Strengths.
14. Assumptions register.
15. Follow-on assurance scope.
16. Architect questionnaire.
17. Re-review triggers.
18. Catalogue delta.
19. Appendix: input inventory, intelligence log with URLs and access dates, simulation command lines.

## Diagrams

**Annotated MSCs.** Copy each flow and, after every message that has a finding or an open question, add
`Note over A,B: FND-03 High - short title` (or `Q-F1.M3-02 OPEN`). Wrap messages tied to Critical or High findings in `rect rgb(255,220,220)` ... `end`, Medium in `rect rgb(255,240,200)`. Keep notes short. Do not use `;` or `#` in labels.

**Rendering with mermaid-cli** (`mmdc`). It needs a Chrome or Chromium binary; write a puppeteer config pointing at it:

```
echo '{"executablePath":"/path/to/chrome","args":["--no-sandbox"]}' > review/p.json
mmdc -p review/p.json -i diagrams/F1.mmd -o diagrams/F1.svg -q
mmdc -p review/p.json -i diagrams/F1.mmd -o diagrams/F1.pdf -f -q
mmdc -p review/p.json -i diagrams/F1.mmd -o diagrams/F1.png -s 2 -q
```

Install with `npm install -g @mermaid-js/mermaid-cli` if missing and installation is permitted.

## Rendering the report

In `report.md`, write each image as `![caption](diagrams/F1.IMG)` followed by a blank line and the caption in italics (`*caption*`). The `.IMG` placeholder is swapped per target. Run from the `review/` directory:

```
F='-f markdown-implicit_figures'
mkdir -p out/diagrams && cp diagrams/*.svg diagrams/*.mmd out/diagrams/
sed 's/\.IMG)/.svg)/g' report.md > out/report.md
sed 's/\.IMG)/.svg)/g' report.md | pandoc $F -s --embed-resources --toc --metadata title="TITLE" -o out/report.html
sed 's/\.IMG)/.pdf)/g' report.md | pandoc $F -s --toc -V geometry:margin=2cm -V papersize=a4 -o out/report.tex
sed 's/\.IMG)/.pdf)/g' report.md | pandoc $F --pdf-engine=xelatex --toc -V geometry:margin=2cm -V papersize=a4 -V fontsize=10pt -V mainfont="DejaVu Serif" -V sansfont="DejaVu Sans" -V monofont="DejaVu Sans Mono" -o out/report.pdf
sed 's/\.IMG)/.png)/g' report.md | pandoc $F --toc -o out/report.docx
```

Why these options (each fixes a fault seen in testing):
- **`-f markdown-implicit_figures`** keeps diagrams inline, in order, next to their findings. Without it LaTeX treats them as floats and several in a row can run off the page.
- **`mainfont`** must be an installed Unicode font. The default LaTeX font silently drops symbols such as ≤ and →. Check with `fc-list`; good choices are DejaVu Serif, Noto Serif, Cambria or Times New Roman. If none is available, omit the three font options and avoid non-ASCII symbols. Search the pandoc output for "Missing character" either way.
- **`papersize`**: `a4` or `letter` to suit the reader.
- On Windows without `sed`, do the `.IMG` replacement with any text tool (PowerShell `-replace`, Python) and pass the file to pandoc.

- **LaTeX:** ship `report.tex` with the diagram PDFs in `diagrams/`. On request, also emit the flows as native LaTeX charts using the `msc` package.
- **DOCX:** add `--reference-doc=TEMPLATE.docx` when the user supplies a house template.
- **Tables:**
  - At most six or seven columns per table in the report. The full sixteen-column step table and the traceability matrix go in `out/step-table.csv` and `out/traceability.csv`; the report shows them split by theme (who talks to whom and how they authenticate; integrity, freshness and fault behaviour; state and invariants).
  - Use pipe tables and set relative column widths with the number of dashes in the separator row, giving more to prose columns. Cells wrap only when a source row is longer than the line width, which real rows are.
  - Give a column holding long unbreakable tokens (`UNSPECIFIED`, IDs) enough width, or the token overruns its neighbour.

## Jira CSV

Columns: `Summary, Description, Priority, Labels, Invariant, Unit ID, Severity, Source Ref`.
Priority mapping: Critical -> Highest, High -> High, Medium -> Medium, Low -> Low, Informational -> Lowest.
Description holds attack path, preconditions, minimal compromise set, recommendation and fix-verification criterion. Quote every field; escape embedded quotes by doubling them.

## Other deliverables

- Architect questionnaire as a separate Markdown or DOCX file, grouped by flow and unit.
- Simulation bundle: engine, model files, `results.json`, counterexample `.mmd` files.

## When tools are missing

- **No mermaid-cli or no browser:** keep diagrams as fenced `mermaid` code blocks in the Markdown and HTML (many viewers render them) and ship the `.mmd` sources; tell the user PDF and DOCX carry diagram source instead of images.
- **No LaTeX engine:** produce HTML, DOCX and Markdown; offer the `.tex` source for the user to compile.
- **No pandoc:** deliver `report.md`, the CSV and the questionnaire, and say which formats could not be produced.
- Never claim a format was produced without opening the output.

## Checks before delivery

- Every finding ID appears in the report, in the CSV, and on at least one diagram.
- Every unit in the step table appears in its diagram and in the model's `messages`.
- Every external fact in the report has an intelligence-log entry with a URL and access date.
- The PDF opens; page count is sensible; diagrams are present and complete; no table or figure runs off the page; the pandoc output has no "Missing character" or "Overfull \vbox" warnings. Render a page to an image and look at it.
- DOCX and HTML show their images.
- The report header states the simulation bounds and whether the intelligence refresh ran.
