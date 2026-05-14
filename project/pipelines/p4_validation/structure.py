from domain.report_layout import REQUIRED_SECTIONS


def validate(report: str) -> list[str]:
    return [f"seção '{s}' ausente" for s in REQUIRED_SECTIONS if s not in report]
