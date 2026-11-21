RAVEN-MCS IEEE TMC Overleaf package
====================================

Upload this zip to Overleaf (New Project -> Upload Project).
The project root contains main.tex.

Compile
-------
1. Menu -> Compiler: pdfLaTeX. TeX Live 2024 or 2025 is fine.
2. Set the main document to main.tex and compile (bibtex will run automatically).
3. To inspect the supplemental PDF: set the main document to supplemental.tex
   and compile AFTER main.tex has been compiled once. supplemental.tex uses
   the xr package and needs main.aux from the companion paper.
4. Download each PDF separately. IEEE TMC wants the supplemental file as a
   separate PDF, not merged into the main paper.

Included
--------
- main.tex          body
- appendix.tex      proofs and extra tables (input by supplemental.tex)
- supplemental.tex  separate supplemental document
- reference.bib
- figures/*.pdf     all figures used by main or supplemental

Not included
------------
LaTeX aux/log files, PNG previews, make_figures.py, internal review notes.

Author names in the tex files still contain **** placeholders.
