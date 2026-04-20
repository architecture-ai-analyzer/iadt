Analise este diagrama de arquitetura e extraia sua estrutura.

Retorne SOMENTE um objeto JSON válido, sem texto adicional, sem markdown, sem explicações.

O JSON deve seguir exatamente este schema:

```json
{
  "components": [
    {"name": "<nome do componente>", "type": "<tipo>"}
  ],
  "relationships": [
    {"from": "<componente origem>", "to": "<componente destino>", "label": "<protocolo ou descrição>"}
  ],
  "uncertainties": [
    "<descrição de ambiguidade ou elemento que não foi possível confirmar>"
  ]
}
```

Tipos válidos para `type`: gateway, service, database, queue, cache, load_balancer, external, client, storage, unknown

Regras:
- Inclua APENAS componentes visíveis no diagrama. Não invente.
- `relationships` pode ser lista vazia se não houver conexões visíveis.
- `uncertainties` deve listar qualquer elemento ambíguo ou não confirmado.
- `label` em relationships é opcional; omita se não houver texto na seta.
- Nomes devem preservar o texto original do diagrama quando legível.
