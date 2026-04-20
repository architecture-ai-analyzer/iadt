REQUIRED_SECTIONS = [
    "## 1. Resumo executivo",
    "## 2. Componentes identificados",
    "## 3. Relações observadas",
    "## 4. Riscos arquiteturais",
    "## 5. Recomendações",
    "## 6. Limitações da análise",
    "## 7. Nível de confiança",
]


def validate(report: str) -> list[str]:
    return [f"seção '{s}' ausente" for s in REQUIRED_SECTIONS if s not in report]
