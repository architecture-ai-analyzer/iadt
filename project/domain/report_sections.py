"""Extrai o corpo de cada seção do relatório Markdown."""

from __future__ import annotations

from dataclasses import dataclass, field

from domain.report_layout import SECTION_DEFINITIONS


def _content_start_after_header(text: str, header_start: int, header_len: int) -> int:
    pos = header_start + header_len
    if pos < len(text) and text[pos] == "\n":
        return pos + 1
    return pos


@dataclass
class SectionParseResult:
    """Resultado do parse por cabeçalhos `## N. ...`."""

    sections: dict[str, str] = field(default_factory=dict)
    missing_headers: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing_headers and len(self.sections) == len(SECTION_DEFINITIONS)


def markdown_to_structured_sections(report: str) -> SectionParseResult:
    """
    Localiza cada cabeçalho conhecido no texto e extrai o bloco até o próximo cabeçalho
    `##` (ou fim do arquivo). Ordem no arquivo pode diferir da ordem canônica.
    """
    positions: list[tuple[int, str, str, int]] = []
    missing: list[str] = []
    for header, key in SECTION_DEFINITIONS:
        idx = report.find(header)
        if idx == -1:
            missing.append(header)
        else:
            positions.append((idx, key, header, len(header)))

    if missing:
        return SectionParseResult(sections={}, missing_headers=missing)

    positions.sort(key=lambda t: t[0])
    sections: dict[str, str] = {}
    for i, (start, key, header, hlen) in enumerate(positions):
        cstart = _content_start_after_header(report, start, hlen)
        if i + 1 < len(positions):
            end = positions[i + 1][0]
            body = report[cstart:end].strip()
        else:
            body = report[cstart:].strip()
        sections[key] = body

    return SectionParseResult(sections=sections, missing_headers=[])
