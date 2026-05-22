"""Mapeia JSON enriquecido do pipeline para o contrato de saída da fila SQS."""

from __future__ import annotations

import re
from typing import Any

_COMPONENT_TYPE_MAP: dict[str, str] = {
    "gateway": "API",
    "service": "SERVICE",
    "function": "FUNCTION",
    "database": "DATABASE",
    "queue": "MESSAGING",
    "cache": "CACHE",
    "load_balancer": "LOAD_BALANCER",
    "external": "EXTERNAL",
    "client": "FRONTEND",
    "storage": "STORAGE",
    "connector": "INTEGRATION",
    "unknown": "UNKNOWN",
}

_CONCERN_CATEGORY_MAP: dict[str, str] = {
    "availability": "RELIABILITY",
    "security": "SECURITY",
    "scalability": "PERFORMANCE",
    "coupling": "RELIABILITY",
    "data": "DATA",
    "operational": "OPERATIONAL",
    "other": "OTHER",
}

_SEVERITY_LEVEL: dict[str, str] = {
    "high": "HIGH",
    "medium": "MEDIUM",
    "low": "LOW",
}

_SEVERITY_SCORE: dict[str, int] = {
    "high": 8,
    "medium": 6,
    "low": 3,
}

_EFFORT_BY_SEVERITY: dict[str, str] = {
    "high": "HIGH",
    "medium": "MEDIUM",
    "low": "LOW",
}


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower().strip())
    return s.strip("-") or "unknown"


def _comp_id(name: str) -> str:
    return f"comp-{_slug(name)}"


def _empty_analysis() -> dict[str, list[Any]]:
    return {"components": [], "risks": [], "recommendations": []}


def build_analysis_from_enriched(enriched: dict[str, Any] | None) -> dict[str, Any]:
    """Converte enriched (P2) em { components, risks, recommendations }."""
    if not enriched:
        return _empty_analysis()

    id_by_name: dict[str, str] = {
        c["name"]: _comp_id(c["name"])
        for c in enriched.get("components", [])
        if c.get("name")
    }

    connections_by_name: dict[str, set[str]] = {name: set() for name in id_by_name}
    for rel in enriched.get("relationships", []):
        src = rel.get("from")
        tgt = rel.get("to")
        if not src or not tgt:
            continue
        if src in connections_by_name and tgt in id_by_name:
            connections_by_name[src].add(id_by_name[tgt])
        if tgt in connections_by_name and src in id_by_name:
            connections_by_name[tgt].add(id_by_name[src])

    components: list[dict[str, Any]] = []
    for comp in enriched.get("components", []):
        name = comp.get("name") or ""
        if not name:
            continue
        cid = id_by_name.get(name, _comp_id(name))
        props: dict[str, Any] = {}
        for key in ("subtype", "role", "provider"):
            if comp.get(key):
                props[key] = comp[key]
        if comp.get("is_managed_service") is not None:
            props["isManagedService"] = comp["is_managed_service"]
        if comp.get("confidence") is not None:
            props["confidence"] = comp["confidence"]
        evidence = comp.get("evidence") or {}
        for ek, ev in evidence.items():
            if ev:
                props[ek] = ev

        technology = comp.get("subtype") or comp.get("provider") or comp.get("type", "unknown")
        description_parts = [comp.get("role"), (evidence or {}).get("label_text")]
        description = " — ".join(p for p in description_parts if p) or name

        components.append({
            "id": cid,
            "name": name,
            "type": _COMPONENT_TYPE_MAP.get(comp.get("type", "unknown"), "UNKNOWN"),
            "connections": sorted(connections_by_name.get(name, set())),
            "properties": props,
            "technology": str(technology),
            "description": description,
        })

    risks: list[dict[str, Any]] = []
    for concern in enriched.get("concerns", []):
        affected = concern.get("affected_components") or []
        affected_id = id_by_name.get(affected[0], _comp_id(affected[0])) if affected else ""
        severity = concern.get("severity", "medium")
        category = concern.get("category", "other")
        risks.append({
            "id": f"risk-{_slug(concern.get('id') or concern.get('title', 'unknown'))}",
            "description": concern.get("description") or concern.get("title", ""),
            "level": _SEVERITY_LEVEL.get(severity, "MEDIUM"),
            "affectedComponent": affected_id,
            "category": _CONCERN_CATEGORY_MAP.get(category, "OTHER"),
            "mitigation": _mitigation_for_concern(concern, category),
            "severityScore": _SEVERITY_SCORE.get(severity, 5),
            "impact": concern.get("title") or concern.get("description", ""),
        })

    recommendations: list[dict[str, Any]] = []
    for concern in enriched.get("concerns", []):
        affected = concern.get("affected_components") or []
        target_id = id_by_name.get(affected[0], _comp_id(affected[0])) if affected else ""
        severity = concern.get("severity", "medium")
        category = concern.get("category", "other")
        recommendations.append({
            "id": f"rec-{_slug(concern.get('id') or concern.get('title', 'unknown'))}",
            "description": concern.get("title") or "Recomendação arquitetural",
            "targetComponent": target_id,
            "type": _CONCERN_CATEGORY_MAP.get(category, "OTHER"),
            "priority": _SEVERITY_LEVEL.get(severity, "MEDIUM"),
            "rationale": concern.get("description", ""),
            "effort": _EFFORT_BY_SEVERITY.get(severity, "MEDIUM"),
            "steps": _mitigation_for_concern(concern, category),
        })

    return {
        "components": components,
        "risks": risks,
        "recommendations": recommendations,
    }


def _mitigation_for_concern(concern: dict[str, Any], category: str) -> list[str]:
    title = (concern.get("title") or "").strip()
    if title:
        return [
            f"Analisar e tratar: {title}",
            "Definir plano de implementação com critérios de aceite",
            "Monitorar indicadores após a mudança",
        ]
    templates: dict[str, list[str]] = {
        "availability": [
            "Implementar redundância ou failover",
            "Adicionar health checks e alertas",
            "Validar recuperação em testes de caos",
        ],
        "security": [
            "Revisar controles de acesso e autenticação",
            "Aplicar princípio do menor privilégio",
            "Auditar exposição de superfície de ataque",
        ],
        "scalability": [
            "Dimensionar capacidade com métricas de carga",
            "Introduzir auto-scaling ou filas de absorção",
            "Testar limites sob pico de tráfego",
        ],
    }
    return templates.get(category, [
        "Investigar causa raiz do risco identificado",
        "Implementar controles adequados",
        "Validar em ambiente de teste",
    ])
