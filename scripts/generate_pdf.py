"""
Convierte archivos Markdown a PDF estilizado usando fpdf2 con fuentes Unicode.
Uso:
  python scripts/generate_pdf.py                          # README.md → README.pdf
  python scripts/generate_pdf.py --input docs/MANUAL_ETL.md --output docs/MANUAL_ETL.pdf
  python scripts/generate_pdf.py --all-docs               # Convierte todos los .md de docs/
"""

import argparse
import re
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

FONTS_DIR = Path("/System/Library/Fonts/Supplemental")

COLORS = {
    "h1":        (30,  30,  60),
    "h2":        (20,  80, 160),
    "h3":        (50, 130, 200),
    "body":      (40,  40,  40),
    "code_bg":   (245, 245, 248),
    "code_text": (50,  50,  50),
    "table_hdr": (20,  80, 160),
    "table_alt": (240, 246, 255),
    "table_brd": (200, 210, 230),
    "hr":        (180, 190, 210),
    "white":     (255, 255, 255),
    "link":      (0,  100, 200),
    "quote_bg":  (240, 244, 255),
    "quote_bar": (20,  80, 160),
}


class ReadmePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)

        self.add_font("Arial",      "",   str(FONTS_DIR / "Arial.ttf"))
        self.add_font("Arial",      "B",  str(FONTS_DIR / "Arial Bold.ttf"))
        self.add_font("Arial",      "I",  str(FONTS_DIR / "Arial Italic.ttf"))
        self.add_font("Arial",      "BI", str(FONTS_DIR / "Arial Bold Italic.ttf"))
        self.add_font("CourierNew", "",   str(FONTS_DIR / "Courier New.ttf"))
        self.add_font("CourierNew", "B",  str(FONTS_DIR / "Courier New Bold.ttf"))

        self.add_page()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _c(self, key: str) -> tuple:
        return COLORS[key]

    def _clean(self, text: str) -> str:
        """Elimina sintaxis markdown residual del texto plano."""
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"`(.+?)`", r"\1", text)
        return text.strip()

    def _write_inline(self, line: str, base_size: float, plain_style: str = ""):
        """Renderiza línea con **negrita** e `inline code` correctamente."""
        parts = re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", line)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                self.set_font("Arial", "B", base_size)
                self.set_text_color(*self._c("body"))
                self.write(h=base_size * 0.45, text=part[2:-2])
            elif part.startswith("`") and part.endswith("`"):
                self.set_font("CourierNew", "", base_size - 0.5)
                self.set_text_color(*self._c("code_text"))
                self.write(h=base_size * 0.45, text=part[1:-1])
            else:
                self.set_font("Arial", plain_style, base_size)
                self.set_text_color(*self._c("body"))
                clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", part)
                self.write(h=base_size * 0.45, text=clean)
        self.set_font("Arial", "", base_size)
        self.set_text_color(*self._c("body"))

    def _count_lines(self, text: str, width: float) -> int:
        """Estima el número de líneas que ocupará el texto con el font actual."""
        if not text.strip() or width <= 0:
            return 1
        words = text.split()
        if not words:
            return 1
        lines = 1
        current_w = 0.0
        for word in words:
            word_w = self.get_string_width(word + " ")
            if current_w + word_w > width and current_w > 0:
                lines += 1
                current_w = word_w
            else:
                current_w += word_w
        return lines

    # ── headings ─────────────────────────────────────────────────────────────

    def render_h1(self, text: str):
        self.ln(6)
        self.set_fill_color(*self._c("h1"))
        self.set_text_color(*self._c("white"))
        self.set_font("Arial", "B", 20)
        self.cell(0, 13, self._clean(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(4)

    def render_h2(self, text: str):
        self.ln(5)
        self.set_font("Arial", "B", 13)
        self.set_text_color(*self._c("h2"))
        self.cell(0, 8, self._clean(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*self._c("h2"))
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def render_h3(self, text: str):
        self.ln(3)
        self.set_font("Arial", "B", 10)
        self.set_text_color(*self._c("h3"))
        self.cell(0, 7, self._clean(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    # ── párrafo ──────────────────────────────────────────────────────────────

    def render_paragraph(self, text: str):
        if not text.strip():
            return
        self.set_font("Arial", "", 9)
        self.set_text_color(*self._c("body"))
        self._write_inline(text, 9)
        self.ln(5)

    # ── blockquote ───────────────────────────────────────────────────────────

    def render_blockquote(self, text: str):
        self.ln(2)
        x, y = self.l_margin, self.get_y()
        inner_x = x + 8
        inner_w = self.w - self.l_margin - self.r_margin - 8

        self.set_font("Arial", "I", 8.5)
        self.set_text_color(*self._c("body"))
        self.set_fill_color(*self._c("quote_bg"))
        self.set_draw_color(*self._c("quote_bg"))

        self.set_xy(inner_x, y)
        self.multi_cell(inner_w, 5.5, text, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        y_end = self.get_y()
        self.set_draw_color(*self._c("quote_bar"))
        self.set_line_width(2.5)
        self.line(x + 2, y, x + 2, y_end)
        self.set_line_width(0.3)
        self.ln(3)

    # ── código ───────────────────────────────────────────────────────────────

    def render_code_block(self, lines: list[str]):
        if not lines:
            return
        self.ln(2)
        line_h = 4.5
        pad = 3
        self.set_font("CourierNew", "", 7.5)

        inner_w = self.w - self.l_margin - self.r_margin - pad * 2

        # Expandir líneas que desborden el ancho disponible
        expanded: list[str] = []
        char_w = self.get_string_width("M") or 4.2
        max_chars = max(1, int(inner_w / char_w))

        for code_line in lines:
            if not code_line:
                expanded.append("")
                continue
            if self.get_string_width(code_line) <= inner_w:
                expanded.append(code_line)
            else:
                while len(code_line) > max_chars:
                    expanded.append(code_line[:max_chars])
                    code_line = "    " + code_line[max_chars:]
                expanded.append(code_line)

        block_h = len(expanded) * line_h + pad * 2
        x, y = self.l_margin, self.get_y()
        w = self.w - self.l_margin - self.r_margin

        self.set_fill_color(*self._c("code_bg"))
        self.set_draw_color(*self._c("table_brd"))
        self.set_line_width(0.3)
        self.rect(x, y, w, block_h, style="FD")

        self.set_font("CourierNew", "", 7.5)
        self.set_text_color(*self._c("code_text"))
        self.set_xy(x + pad, y + pad)

        for code_line in expanded:
            self.cell(w - pad * 2, line_h, code_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_x(x + pad)

        self.ln(4)

    # ── lista ────────────────────────────────────────────────────────────────

    def render_list_item(self, text: str, level: int = 0):
        indent = self.l_margin + level * 6
        self.set_x(indent)
        self.set_font("Arial", "", 9)
        self.set_text_color(*self._c("body"))
        bullet = "•" if level == 0 else "◦"
        self.cell(5, 5, bullet)
        self._write_inline(text.strip(), 9)
        self.ln(5)
        self.set_x(self.l_margin)

    # ── separador ────────────────────────────────────────────────────────────

    def render_hr(self):
        self.ln(3)
        self.set_draw_color(*self._c("hr"))
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    # ── tabla ────────────────────────────────────────────────────────────────

    def render_table(self, rows: list[list[str]]):
        if not rows:
            return
        self.ln(2)
        usable_w = self.w - self.l_margin - self.r_margin
        col_count = max(len(r) for r in rows)
        col_w = usable_w / col_count
        line_h = 5.5
        cell_pad = 2.0  # margen interno que usa fpdf2 en multi_cell
        self.set_line_width(0.2)

        for row_idx, row in enumerate(rows):
            while len(row) < col_count:
                row.append("")

            is_header = row_idx == 0
            is_alt    = (not is_header) and (row_idx % 2 == 0)

            # Calcular font para estimar líneas correctamente
            if is_header:
                self.set_font("Arial", "B", 8)
            else:
                self.set_font("Arial", "", 8)

            # Pre-calcular altura real de la fila (max de todas las celdas)
            max_lines = 1
            for cell_text in row:
                nb = self._count_lines(cell_text.strip(), col_w - cell_pad)
                max_lines = max(max_lines, nb)
            actual_row_h = max_lines * line_h + 1  # +1mm de buffer

            # Verificar salto de página antes de renderizar la fila completa
            if self.will_page_break(actual_row_h + 4):
                self.add_page()

            # Aplicar estilo visual
            if is_header:
                self.set_fill_color(*self._c("table_hdr"))
                self.set_text_color(*self._c("white"))
                self.set_font("Arial", "B", 8)
                fill = True
            elif is_alt:
                self.set_fill_color(*self._c("table_alt"))
                self.set_text_color(*self._c("body"))
                self.set_font("Arial", "", 8)
                fill = True
            else:
                self.set_fill_color(*self._c("white"))
                self.set_text_color(*self._c("body"))
                self.set_font("Arial", "", 8)
                fill = False

            self.set_draw_color(*self._c("table_brd"))
            x_start = self.l_margin
            y_row = self.get_y()

            for cell_text in row:
                self.set_xy(x_start, y_row)
                self.multi_cell(
                    col_w, line_h,
                    cell_text.strip(),
                    border=1, fill=fill,
                    new_x=XPos.RIGHT, new_y=YPos.TOP,
                )
                x_start += col_w

            # Avanzar Y por la altura real calculada (no un row_h fijo)
            self.set_y(y_row + actual_row_h)

        self.ln(3)
        self.set_text_color(*self._c("body"))


# ── Parser ────────────────────────────────────────────────────────────────────

def _is_separator_row(row: str) -> bool:
    return bool(re.match(r"^\|?[\s\-\|:]+\|?$", row))


def parse_and_render(pdf: ReadmePDF, md_text: str):
    lines = md_text.splitlines()
    i = 0
    para_buf: list[str] = []

    def flush_para():
        if para_buf:
            pdf.render_paragraph(" ".join(para_buf))
            para_buf.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Bloque de código fenced
        if stripped.startswith("```"):
            flush_para()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            pdf.render_code_block(code_lines)
            i += 1
            continue

        # Headings
        if re.match(r"^# [^#]", stripped):
            flush_para()
            pdf.render_h1(stripped[2:])
            i += 1
            continue
        if re.match(r"^## [^#]", stripped):
            flush_para()
            pdf.render_h2(stripped[3:])
            i += 1
            continue
        if re.match(r"^### [^#]", stripped):
            flush_para()
            pdf.render_h3(stripped[4:])
            i += 1
            continue

        # Separador HR
        if re.match(r"^[-*_]{3,}$", stripped):
            flush_para()
            pdf.render_hr()
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            flush_para()
            bq_text = stripped.lstrip(">").strip()
            bq_text = re.sub(r"\*\*(.+?)\*\*", r"\1", bq_text)
            bq_text = re.sub(r"\*(.+?)\*",     r"\1", bq_text)
            bq_text = re.sub(r"`(.+?)`",        r"\1", bq_text)
            bq_text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", bq_text)
            pdf.render_blockquote(bq_text)
            i += 1
            continue

        # Tabla
        if stripped.startswith("|") and "|" in stripped[1:]:
            flush_para()
            table_rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                raw_row = lines[i].strip().strip("|")
                cells = [c.strip() for c in raw_row.split("|")]
                if not _is_separator_row(lines[i]):
                    table_rows.append(cells)
                i += 1
            pdf.render_table(table_rows)
            continue

        # Lista
        m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)", line)
        if m:
            flush_para()
            indent_str, _, item = m.groups()
            pdf.render_list_item(item, level=len(indent_str) // 2)
            i += 1
            continue

        # Línea vacía
        if not stripped:
            flush_para()
            i += 1
            continue

        # Texto plano
        para_buf.append(stripped)
        i += 1

    flush_para()


def generate(input_path: Path, output_path: Path) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"No se encontró: {input_path}")

    md_text = input_path.read_text(encoding="utf-8")
    pdf = ReadmePDF()
    parse_and_render(pdf, md_text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    print(f"PDF generado: {output_path}")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.parent

    parser = argparse.ArgumentParser(description="Convierte Markdown a PDF")
    parser.add_argument("--input",    type=Path, default=None, help="Archivo .md de entrada")
    parser.add_argument("--output",   type=Path, default=None, help="Archivo .pdf de salida")
    parser.add_argument("--all-docs", action="store_true",     help="Convierte todos los .md de docs/")
    args = parser.parse_args()

    if args.all_docs:
        docs_dir = BASE_DIR / "docs"
        md_files = list(docs_dir.glob("*.md"))
        if not md_files:
            print("No se encontraron archivos .md en docs/")
        for md_file in md_files:
            generate(md_file, md_file.with_suffix(".pdf"))
    elif args.input and args.output:
        generate(args.input, args.output)
    else:
        generate(BASE_DIR / "README.md", BASE_DIR / "README.pdf")
