# Estrutura do projeto

Separação por função, não por etapa:

- `.md` = contrato/documentação
- `pipelines/` = lógica executável por etapa
- `orchestrator/` = encadeia e trata erros
- `schemas/` = contrato de dados entre etapas
- `prompts/` = prompts externos, versionáveis
- `llm/` = cliente único para chamadas de modelo
- `tests/` + `samples/` = requisito do hackaton (seções 12 e 13)

## Estrutura

```
project/
│
├─ docs/
│  └─ arquitetura.md                 # único; HACKATON - Pipelines.md é a spec por etapa
│
├─ prompts/
│  ├─ extracao.md                    # P1 — prompt base
│  ├─ extracao_reforcado.md          # P1 — retry com instrução reforçada
│  └─ relatorio.md                   # P3
│
├─ schemas/
│  ├─ canonical.json                 # saída da P1
│  └─ enriched.json                  # saída da P2
│
├─ llm/
│  ├─ client.py                      # abstração retry/timeout/parse JSON
│  ├─ multimodal.py                  # Claude/GPT-4o (P1)
│  └─ text.py                        # Ollama ou API (P3)
│
├─ pipelines/
│  ├─ p1_extraction/
│  │  ├─ __init__.py                 # entrypoint: extract(file) -> canonical
│  │  ├─ classifier.py               # imagem | pdf_exportado | pdf_escaneado
│  │  ├─ image_route.py              # imagem → multimodal
│  │  ├─ pdf_exported_route.py       # texto + imagem → multimodal
│  │  └─ pdf_scanned_route.py        # pdf2image → multimodal
│  │
│  ├─ p2_risk_analysis/
│  │  ├─ __init__.py                 # entrypoint: analyze(canonical) -> enriched
│  │  ├─ registry.py                 # registra e executa regras
│  │  └─ rules/
│  │     ├─ single_point_of_failure.py
│  │     ├─ centralized_database.py
│  │     ├─ missing_edge_auth.py
│  │     ├─ unmediated_external.py
│  │     └─ excessive_coupling.py
│  │
│  ├─ p3_report_generation/
│  │  └─ __init__.py                 # entrypoint: generate(enriched) -> markdown
│  │
│  └─ p4_validation/
│     ├─ __init__.py                 # entrypoint: validate(report, enriched) -> result
│     ├─ structure.py                # seções obrigatórias
│     └─ consistency.py              # componentes/riscos cruzados
│
├─ orchestrator/
│  └─ pipeline.py                    # encadeia P1→P2→P3→P4, estado, erros
│
├─ config/
│  ├─ settings.py                    # lê .env (API keys, endpoint Ollama, modelos)
│  └─ logging.py                     # logging JSON estruturado
│
├─ tests/
│  ├─ test_p1_extraction.py
│  ├─ test_p2_risk_analysis.py
│  ├─ test_p3_report_generation.py
│  ├─ test_p4_validation.py
│  └─ test_orchestrator.py           # ponta a ponta
│
├─ samples/                          # 3-5 diagramas de teste (seção 13)
│  ├─ diagram_01.png
│  ├─ diagram_02.pdf
│  └─ ...
│
├─ runs/                             # saída de execuções (logs JSON, relatórios)
│  └─ .gitkeep
│
├─ cli.py                            # entrypoint: python cli.py <arquivo>
├─ .env.example
├─ pyproject.toml                    # ou requirements.txt
└─ README.md
```

## Princípios

1. **Cada pipeline tem 1 entrypoint público** (`__init__.py` com função `run/extract/analyze/...`). Tudo mais é detalhe interno.
2. **Pipelines não conhecem o orquestrador.** Testáveis em isolamento (requisito da seção 12).
3. **Toda chamada a modelo passa por `llm/client.py`.** Retry, timeout e parsing em um lugar só.
4. **Regras de risco seguem registry pattern.** Adicionar regra = criar arquivo novo em `rules/`, sem tocar o pipeline.
5. **Prompts fora do código.** Versionáveis, comparáveis, iteráveis sem deploy.
6. **Schemas JSON são contratos.** P2 e P4 validam contra eles antes de processar.
7. **Documentação por função, não por etapa.** `HACKATON - Pipelines.md` já é a spec por etapa; um `arquitetura.md` mestre basta.

## Ordem de implementação

Segue seção 11 do Pipelines: P1 → P2 → P3 → P4. Antes de P1, criar `llm/client.py`, `schemas/` e `config/` — são dependências horizontais de todas as etapas.
