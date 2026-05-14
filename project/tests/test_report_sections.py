from domain.report_layout import REQUIRED_SECTIONS, SECTION_DEFINITIONS
from domain.report_sections import markdown_to_structured_sections


def _full_report_in_order():
    parts = []
    for header, _key in SECTION_DEFINITIONS:
        parts.append(f"{header}\nTexto da seção para {_key}.")
    return "\n\n".join(parts)


def test_parse_all_sections_in_order():
    text = _full_report_in_order()
    result = markdown_to_structured_sections(text)
    assert result.ok
    assert len(result.sections) == 7
    assert result.sections["executive_summary"].startswith("Texto da seção")
    assert "executive_summary" in result.sections


def test_parse_sections_reordered_in_document():
    headers = [h for h, _ in SECTION_DEFINITIONS]
    # Inverte ordem dos blocos no arquivo
    blocks = [f"{h}\nConteúdo {i}." for i, h in enumerate(reversed(headers))]
    text = "\n\n".join(blocks)
    result = markdown_to_structured_sections(text)
    assert result.ok
    assert result.sections["confidence_level"] == "Conteúdo 0."
    assert result.sections["executive_summary"] == "Conteúdo 6."


def test_missing_section():
    text = "\n\n".join(f"{h}\nX." for h in REQUIRED_SECTIONS[:3])
    result = markdown_to_structured_sections(text)
    assert not result.ok
    assert result.sections == {}
    assert any("## 4." in m for m in result.missing_headers)


def test_section_body_until_next_header():
    parts: list[str] = []
    for i, (h, _k) in enumerate(SECTION_DEFINITIONS):
        if i == 0:
            parts.append(f"{h}\nline a\nline b")
        elif i == 1:
            parts.append(f"{h}\nnext")
        else:
            parts.append(f"{h}\nZ.")
    text = "\n\n".join(parts)
    result = markdown_to_structured_sections(text)
    assert result.ok
    assert "line a" in result.sections["executive_summary"]
    assert "next" not in result.sections["executive_summary"]
