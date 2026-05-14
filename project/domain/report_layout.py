"""Cabeçalhos de seção do relatório (âncora única para P3, P4 e parser SQS)."""

from typing import Final

# (cabeçalho exato no Markdown, chave estável no JSON de saída)
SECTION_DEFINITIONS: Final[list[tuple[str, str]]] = [
    ("## 1. Resumo executivo", "executive_summary"),
    ("## 2. Componentes identificados", "identified_components"),
    ("## 3. Relações observadas", "observed_relationships"),
    ("## 4. Riscos arquiteturais", "architectural_risks"),
    ("## 5. Recomendações", "recommendations"),
    ("## 6. Limitações da análise", "analysis_limitations"),
    ("## 7. Nível de confiança", "confidence_level"),
]

REPORT_SECTION_HEADERS: Final[list[str]] = [h for h, _ in SECTION_DEFINITIONS]

# Alias esperado por validação e testes existentes
REQUIRED_SECTIONS: Final[list[str]] = REPORT_SECTION_HEADERS
