from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ArtworkLabel:
    artwork_id: str
    title: str
    qr_path: Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "oeuvres.json"
QR_DIR = PROJECT_ROOT / "docs" / "assets" / "qrcodes" / "fr"


def remove_latex_unsupported_characters(text: str) -> str:
    cleaned_chars: list[str] = []
    for char in text:
        category = unicodedata.category(char)
        if category in {"Cs", "Co", "Cn"}:
            continue
        if category == "So":
            continue
        if ord(char) > 0xFFFF:
            continue
        cleaned_chars.append(char)
    return "".join(cleaned_chars).strip()


def escape_latex(text: str) -> str:
    text = remove_latex_unsupported_characters(text)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    out = text
    for src, dst in replacements.items():
        out = out.replace(src, dst)
    return out


def load_labels(data_file: Path, qr_dir: Path) -> list[ArtworkLabel]:
    raw = json.loads(data_file.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"{data_file} must contain a list of artworks.")

    labels: list[ArtworkLabel] = []
    missing_qr: list[str] = []

    for item in raw:
        if not isinstance(item, dict):
            continue

        artwork_id = str(item.get("id", "")).strip()
        if not artwork_id:
            continue

        title_data = item.get("title", {})
        if isinstance(title_data, dict):
            title = str(title_data.get("fr", "")).strip()
        else:
            title = str(title_data).strip()

        if not title:
            title = artwork_id

        qr_path = qr_dir / f"{artwork_id}.png"
        if not qr_path.exists():
            missing_qr.append(artwork_id)
            continue

        labels.append(ArtworkLabel(artwork_id=artwork_id, title=title, qr_path=qr_path))

    if missing_qr:
        print("QR codes missing for the following artworks:")
        for artwork_id in missing_qr:
            print(f"  - {artwork_id}")

    if not labels:
        raise ValueError("No valid QR labels found.")

    return labels


def build_latex(
    labels: list[ArtworkLabel],
    columns: int,
    rows: int,
    qr_size_cm: float,
    top_space_cm: float,
) -> str:
    if columns <= 0 or rows <= 0:
        raise ValueError("columns and rows must be positive integers.")

    labels_per_page = columns * rows
    cell_width = round(0.96 / columns, 6)
    column_spec = (f"p{{{cell_width}\\textwidth}}|") * columns
    tabular_open = rf"\begin{{tabular}}{{|{column_spec}}}"

    lines: list[str] = [
        r"\documentclass[a4paper,10pt]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[french]{babel}",
        r"\usepackage[a4paper,margin=1.2cm]{geometry}",
        r"\usepackage{graphicx}",
        r"\usepackage{array}",
        r"\usepackage{tabularx}",
        r"\usepackage{calc}",
        r"\usepackage{ragged2e}",
        r"\usepackage{xcolor}",
        r"\pagestyle{empty}",
        r"\setlength{\parindent}{0pt}",
        r"\setlength{\tabcolsep}{0pt}",
        r"\renewcommand{\arraystretch}{1.0}",
        r"",
        rf"\newcommand{{\QRSize}}{{{qr_size_cm}cm}}",
        rf"\newcommand{{\TopSpace}}{{{top_space_cm}cm}}",
        r"",
        r"\newcommand{\LabelCell}[2]{%",
        r"  \begin{minipage}[t][\dimexpr\TopSpace+\QRSize+1.8cm\relax][t]{\linewidth}%",
        r"    \vspace*{0pt}%",
        r"    \hspace*{0pt}\rule{0pt}{\TopSpace}%",
        r"    \begin{center}%",
        r"      \if\relax\detokenize{#1}\relax",
        r"        \rule{0pt}{\QRSize}\\[0.4em]%",
        r"      \else",
        r"        \includegraphics[width=\QRSize,height=\QRSize,keepaspectratio]{#1}\\[0.4em]%",
        r"      \fi",
        r"      {\large\sffamily\centering #2\par}%",
        r"    \end{center}%",
        r"  \end{minipage}%",
        r"}",
        r"",
        r"\begin{document}",
        r"",
    ]

    for page_start in range(0, len(labels), labels_per_page):
        page_items = labels[page_start : page_start + labels_per_page]

        lines.extend(
            [
                r"\noindent",
                tabular_open,
                r"\hline",
            ]
        )

        for row_index in range(rows):
            row_cells: list[str] = []
            for col_index in range(columns):
                idx = row_index * columns + col_index
                if idx < len(page_items):
                    label = page_items[idx]
                    qr_tex_path = label.qr_path.as_posix()
                    title_tex = escape_latex(label.title)
                    cell = rf"\LabelCell{{{qr_tex_path}}}{{{title_tex}}}"
                else:
                    cell = r"\LabelCell{}{}"
                row_cells.append(cell)

            row_line = " & ".join(row_cells) + r" \\ \hline"
            lines.append(row_line)

        lines.append(r"\end{tabular}")

        if page_start + labels_per_page < len(labels):
            lines.extend([r"\newpage", ""])

    lines.extend([r"", r"\end{document}", ""])
    return "\n".join(lines)


def compile_latex(
    latex_source: str,
    output_pdf: Path,
    keep_tex: bool = False,
) -> None:
    pdflatex = shutil.which("pdflatex")
    if pdflatex is None:
        raise RuntimeError(
            "pdflatex was not found in PATH. Please install a LaTeX distribution."
        )

    output_pdf = output_pdf.resolve()
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="qr_labels_") as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        tex_file = tmpdir / "qr_labels.tex"
        tex_file.write_text(latex_source, encoding="utf-8")

        for _ in range(2):
            result = subprocess.run(
                [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_file.name],
                cwd=tmpdir,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    "LaTeX compilation failed.\n\n"
                    f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
                )

        generated_pdf = tmpdir / "qr_labels.pdf"
        if not generated_pdf.exists():
            raise RuntimeError("LaTeX compilation finished, but no PDF was produced.")

        shutil.copy2(generated_pdf, output_pdf)

        if keep_tex:
            shutil.copy2(tex_file, output_pdf.with_suffix(".tex"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a PDF sheet of QR code labels for artworks."
    )
    parser.add_argument(
        "--columns",
        type=int,
        required=True,
        help="Number of label columns per page.",
    )
    parser.add_argument(
        "--rows",
        type=int,
        required=True,
        help="Number of label rows per page.",
    )
    parser.add_argument(
        "--qr-size",
        type=float,
        default=4.5,
        help="QR code size in cm (default: 4.5).",
    )
    parser.add_argument(
        "--top-space",
        type=float,
        default=2.5,
        help="Empty space above each QR code in cm (default: 2.5).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "qr_labels.pdf",
        help="Output PDF file path.",
    )
    parser.add_argument(
        "--keep-tex",
        action="store_true",
        help="Keep the generated LaTeX file next to the PDF.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    labels = load_labels(DATA_FILE, QR_DIR)
    latex_source = build_latex(
        labels=labels,
        columns=args.columns,
        rows=args.rows,
        qr_size_cm=args.qr_size,
        top_space_cm=args.top_space,
    )
    compile_latex(
        latex_source=latex_source,
        output_pdf=args.output,
        keep_tex=args.keep_tex,
    )
    print(f"PDF generated: {args.output}")


if __name__ == "__main__":
    main()
