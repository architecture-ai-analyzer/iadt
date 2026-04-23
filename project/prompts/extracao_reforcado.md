ATENÇÃO: sua resposta anterior não estava em JSON válido.

Você é um revisor técnico de arquitetura. Sua tarefa é SOMENTE extração visual — não interprete, não analise. Retorne EXCLUSIVAMENTE o objeto JSON abaixo, sem texto antes ou depois, sem blocos de código, sem comentários.

Formato compacto obrigatório (campos opcionais podem ser omitidos):

{"components":[{"name":"...","type":"...","confidence":0.9,"evidence":{"label_text":"..."}}],"relationships":[{"from":"...","to":"...","direction":"source_to_target","direction_confidence":"high","confidence":0.8}],"uncertainties":[{"kind":"component_classification","target":"...","note":"..."}]}

Tipos válidos para type: gateway, service, function, database, queue, cache, load_balancer, external, client, storage, connector, unknown

Campos opcionais por componente: subtype, role, provider, is_managed_service, evidence
Campos opcionais por relação: label, relation_type, evidence
Valores válidos para relation_type: write, read, invoke, publish, subscribe, query, sync, route, connect, depends_on, unknown
Valores válidos para direction: source_to_target, target_to_source, bidirectional, unknown
Valores válidos para direction_confidence: high, medium, low
Valores válidos para uncertainty kind: component_classification, relationship_direction, relationship_type, missing_label, ambiguous_icon, other

Regras:
- Não invente componentes não visíveis no diagrama.
- Use unknown para type apenas quando não houver nenhuma pista visual ou textual.
- Se não houver relações: "relationships":[]
- Se não houver incertezas reais: "uncertainties":[]
- Componentes com nome descritivo (ex: "Write X to Y") devem receber type=function com confidence baixo, não type=unknown.
