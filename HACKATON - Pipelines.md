# Plano de Implementação — Pipelines de IA para Análise de Diagramas de Arquitetura

## 1. Escopo

Este documento cobre exclusivamente o trabalho da equipe IADT no hackathon:

- Processamento do diagrama
- Extração de informações com IA
- Classificação ou análise automatizada
- Geração do conteúdo do relatório
- Avaliação básica da IA

**Fora de escopo**: upload, API, endpoints, banco de dados, filas, storage, consulta de status. O arquivo já está disponível localmente.

---

## 2. Visão geral do pipeline

O sistema é composto por 4 pipelines sequenciais. A saída de cada uma alimenta a entrada da próxima.

```
Arquivo (img/pdf)
    │
    ▼
┌─────────────────────────────┐
│ P1 — Extração               │
│ Entrada: arquivo             │
│ Saída: JSON canônico         │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ P2 — Análise de riscos      │
│ Entrada: JSON canônico       │
│ Saída: JSON enriquecido      │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ P3 — Geração do relatório   │
│ Entrada: JSON enriquecido    │
│ Saída: relatório Markdown    │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ P4 — Validação              │
│ Entrada: relatório + JSON    │
│ Saída: resultado final       │
└─────────────────────────────┘
```

---

## 3. Pipeline 1 — Extração

### O que faz
Recebe o arquivo original, identifica como tratá-lo e extrai componentes, relações e textos do diagrama, produzindo uma estrutura intermediária padronizada.

### Entrada
- arquivo local: `.pdf`, `.png`, `.jpg`, `.jpeg`

### Saída
- JSON canônico:

```json
{
  "components": [
    {"name": "API Gateway", "type": "gateway"},
    {"name": "Auth Service", "type": "service"},
    {"name": "Orders DB", "type": "database"}
  ],
  "relationships": [
    {"from": "API Gateway", "to": "Auth Service", "label": "HTTP"},
    {"from": "Auth Service", "to": "Orders DB", "label": "SQL"}
  ],
  "uncertainties": [
    "Não foi possível confirmar redundância do banco"
  ]
}
```

### Como implementar

Internamente, a pipeline resolve a rota de extração conforme o tipo de arquivo:

**1. Classificação do arquivo (detalhe interno)**
- Se extensão é `.png`, `.jpg`, `.jpeg` → trata como imagem
- Se extensão é `.pdf`:
  - tenta extrair texto com lib programática (`PyMuPDF` ou `pdfplumber`)
  - se há texto relevante → trata como PDF exportado
  - se pouco ou nenhum texto → trata como PDF escaneado

**2. Extração conforme tipo**
- **imagem** → envia direto para API multimodal (Claude/GPT-4o) com prompt estruturado que exige JSON canônico
- **PDF escaneado** → converte para imagem(ns) por página (`pdf2image` ou `PyMuPDF`) → envia para API multimodal
- **PDF exportado** → extrai texto/estrutura programaticamente + envia texto extraído junto com imagem renderizada para API multimodal (contexto textual rico + visão do layout)

### Justificativa
A API multimodal faz extração visual, leitura de texto e interpretação semântica em uma única chamada. A classificação do tipo de arquivo é um detalhe interno de implementação — o que importa para o pipeline é que esta etapa recebe um arquivo e entrega um JSON estruturado. Separar rotas por tipo maximiza a qualidade: PDFs exportados preservam texto nítido que o modelo recebe como contexto adicional, evitando depender apenas de pixels.

### Guardrails
- prompt exige resposta em JSON válido com schema definido
- prompt proíbe inventar componentes não visíveis no diagrama
- prompt exige campo `uncertainties` quando houver ambiguidade

### Tratamento de erros
| Falha | Ação |
|---|---|
| Arquivo não é imagem nem PDF válido | rejeita com motivo: "formato não suportado" |
| API multimodal retorna erro HTTP ou timeout | retry uma vez; se falhar novamente, encerra com erro: "falha na extração — serviço indisponível" |
| API retorna resposta que não é JSON válido | retry uma vez com prompt reforçado; se falhar, encerra com erro: "resposta da IA fora do formato esperado" |
| JSON retornado não tem campo `components` | encerra com erro: "extração incompleta — sem componentes identificados" |
| Conversão PDF→imagem falha | encerra com erro: "falha na conversão do PDF" |

### Logs
- tipo de arquivo recebido e classificação interna (imagem / pdf_exportado / pdf_escaneado)
- rota de extração seguida
- tempo de resposta da API multimodal
- quantidade de componentes e relações extraídos
- warnings (ex: campo `uncertainties` presente)
- erros com motivo

---

## 4. Pipeline 2 — Análise de riscos

### O que faz
Aplica regras determinísticas sobre a estrutura extraída para identificar riscos arquiteturais básicos.

### Entrada
- JSON canônico (vindo da P1)

### Saída
- JSON enriquecido (JSON canônico + riscos):

```json
{
  "components": [...],
  "relationships": [...],
  "uncertainties": [...],
  "risks": [
    {
      "type": "single_point_of_failure",
      "description": "API Gateway é o único ponto de entrada sem redundância aparente",
      "affected_components": ["API Gateway"],
      "severity": "high",
      "evidence": "Apenas um componente do tipo gateway identificado, com múltiplas dependências"
    }
  ]
}
```

### Catálogo de regras (MVP)
1. **Ponto único de falha** — componente com muitas conexões de entrada e sem réplica aparente
2. **Banco centralizado** — um único banco atendendo muitos serviços
3. **Ausência de autenticação em borda** — componente exposto externamente sem menção a auth/gateway
4. **Integração externa sem mediação** — conexão direta com sistema externo sem componente intermediário
5. **Acoplamento excessivo** — componente com número de conexões acima de threshold

### Justificativa
Regras determinísticas são explicáveis e repetíveis. O mesmo JSON sempre produz os mesmos riscos. Isso complementa o LLM (que é probabilístico) com uma camada previsível e auditável.

### Guardrails
- todo risco precisa de `evidence` (não pode apontar risco sem justificativa)
- severity limitada a valores fixos: `low`, `medium`, `high`
- se nenhum risco for encontrado, retorna lista vazia (não inventa)

### Tratamento de erros
| Falha | Ação |
|---|---|
| JSON de entrada sem campo `components` | encerra com erro: "JSON de entrada inválido para análise de riscos" |
| JSON de entrada sem campo `relationships` | processa apenas riscos que não dependem de relações; registra warning |
| Erro interno na execução de uma regra | pula a regra com falha, registra warning, continua com as demais |

### Logs
- quantidade de componentes e relações recebidos
- cada regra executada e seu resultado (risco encontrado ou não)
- quantidade total de riscos identificados com distribuição por severity
- warnings (ex: regra pulada por erro, campo ausente)

---

## 5. Pipeline 3 — Geração do relatório

### O que faz
Gera o relatório técnico estruturado a partir dos dados já extraídos e analisados.

### Entrada
- JSON enriquecido (vindo da P2)

### Saída
- relatório técnico em Markdown com a seguinte estrutura:

```markdown
# Relatório de Análise de Arquitetura

## 1. Resumo executivo
[síntese da análise]

## 2. Componentes identificados
[lista de componentes com tipo e descrição]

## 3. Relações observadas
[conexões entre componentes]

## 4. Riscos arquiteturais
[riscos identificados com severidade e evidência]

## 5. Recomendações
[sugestões práticas para mitigar os riscos]

## 6. Limitações da análise
[o que o sistema não conseguiu determinar]

## 7. Nível de confiança
[avaliação geral da confiabilidade da análise]
```

### Como implementar
- LLM recebe o JSON enriquecido + prompt com instruções de formato
- o LLM **sintetiza**, não extrai — toda informação já está no JSON
- pode usar Ollama local (Llama 3, Mistral, Qwen) ou API — não precisa de visão, é texto→texto

### Justificativa
O relatório nasce de dados já estruturados e validados, não da imagem bruta. Isso reduz alucinação e garante consistência. A separação entre extração (P1) e geração (P3) é o ponto central do pipeline: o LLM recebe fatos, não interpreta pixels.

### Guardrails
- prompt proíbe inventar componentes ou riscos não presentes no JSON
- prompt exige todas as seções do template
- prompt exige seção de limitações mesmo quando a análise parece completa
- formato de saída fixo (Markdown com headers definidos)

### Tratamento de erros
| Falha | Ação |
|---|---|
| LLM retorna erro HTTP ou timeout | retry uma vez; se falhar, encerra com erro: "falha na geração do relatório — serviço indisponível" |
| LLM retorna texto vazio | retry uma vez; se falhar, encerra com erro: "LLM retornou resposta vazia" |
| LLM retorna relatório sem seções obrigatórias | retry uma vez com prompt reforçado; se falhar, encerra com erro: "relatório incompleto" |

### Logs
- modelo LLM utilizado
- tempo de resposta do LLM
- tamanho do relatório gerado (caracteres)
- seções presentes no relatório
- erros com motivo

---

## 6. Pipeline 4 — Validação

### O que faz
Valida a saída final antes de considerá-la pronta.

### Entrada
- relatório Markdown (vindo da P3)
- JSON enriquecido (vindo da P2)

### Saída
- resultado final validado
- ou rejeição com motivo

### Validações
1. **Estrutura do relatório**: todas as 7 seções obrigatórias estão presentes
2. **Consistência**: componentes mencionados no relatório existem no JSON
3. **Completude**: nenhum risco do JSON foi omitido no relatório
4. **Formato**: relatório segue Markdown válido

### Justificativa
Validação automática é a última barreira antes da entrega. Garante que o pipeline não entregou lixo mesmo que alguma etapa anterior tenha falhado parcialmente.

### Tratamento de erros
| Falha | Ação |
|---|---|
| Seção obrigatória ausente no relatório | rejeita com motivo: "seção X ausente" |
| Componente no relatório que não existe no JSON | rejeita com motivo: "componente fabricado detectado — Y mencionado no relatório mas ausente na extração" |
| Risco do JSON omitido no relatório | rejeita com motivo: "risco Z não foi incluído no relatório" |
| Markdown malformado | rejeita com motivo: "formato do relatório inválido" |

### Logs
- resultado da validação (aprovado / rejeitado)
- lista de validações executadas com resultado individual
- motivo da rejeição, se aplicável

---

## 7. Requisitos de IA atendidos

| Requisito do enunciado | Como atendemos |
|---|---|
| Detecção de componentes arquiteturais em imagens | P1 — API multimodal extrai componentes do diagrama |
| Classificação de riscos a partir de regras + ML | P1 (ML — API multimodal extrai a estrutura) + P2 (regras determinísticas classificam riscos sobre essa estrutura) |
| LLM para geração de relatório com guardrails | P3 — LLM com prompt controlado, formato fixo, restrições |
| Análise textual com prompt engineering | P1 + P3 — prompts estruturados com restrições de formato; P4 — avaliação de consistência das respostas |
| Pipeline claro de IA | 4 pipelines sequenciais com entrada/saída definidas |
| Justificativa da abordagem | cada pipeline tem justificativa técnica |
| Demonstração prática | execução ponta a ponta com artefatos intermediários visíveis |
| Discussão de limitações | seção obrigatória no relatório + seção 10 deste documento |

---

## 8. Stack de IA

| Componente | Tecnologia | Justificativa |
|---|---|---|
| Classificação de tipo de arquivo | `PyMuPDF` / `pdfplumber` | extração de texto de PDF sem IA, leve e confiável |
| Conversão PDF escaneado → imagem | `pdf2image` / `PyMuPDF` | lib simples, sem dependência pesada |
| Extração (visão) | API multimodal (Claude / GPT-4o) | melhor qualidade de extração visual; custo ~$0.01/imagem |
| Análise de riscos | Python puro (regras) | determinístico, sem dependência de modelo |
| Geração de relatório | Ollama local (Llama 3 / Mistral / Qwen) ou API | texto→texto, não precisa de visão |
| Validação | Python puro (checagem de schema/formato) | determinístico, sem dependência de modelo |
| Logs | `logging` (Python stdlib) com formato estruturado (JSON) | sem dependência extra, fácil de integrar com observabilidade |

---

## 9. Segurança da IA

### Validação e tratamento de entradas não confiáveis
- P1 valida extensão do arquivo antes de qualquer processamento
- P1 rejeita arquivos que não são imagem nem PDF válido
- P2 valida schema do JSON de entrada antes de aplicar regras
- nenhum dado do usuário é passado diretamente ao prompt sem tratamento

### Uso controlado de modelos de IA
- prompts da P1 e P3 têm escopo fixo: extrair estrutura ou sintetizar relatório
- prompts incluem restrições explícitas (não inventar, não extrapolar)
- formato de saída é definido por schema (P1) e template (P3)
- modelos são chamados com temperature baixa para maximizar previsibilidade

### Tratamento seguro de falhas da IA
- toda chamada a modelo (P1, P3) tem retry limitado (máximo 1 retry)
- respostas fora do formato esperado são rejeitadas, não aproveitadas parcialmente
- falhas resultam em erro explícito com motivo, nunca em saída silenciosamente degradada
- P4 é a última barreira: mesmo que P1 ou P3 falhem parcialmente, a validação detecta

### Riscos e limitações de segurança
- diagramas podem conter dados sensíveis (IPs, nomes de serviços internos) que são enviados à API externa — risco mitigado se usar Ollama local para P3
- prompt injection: um diagrama malicioso poderia conter texto que tenta manipular o prompt — mitigado pelo schema fixo de saída e validação na P4
- a API multimodal é um serviço externo: disponibilidade e latência não estão sob nosso controle
- o LLM pode gerar recomendações incorretas ou genéricas — mitigado pela seção obrigatória de limitações no relatório

---

## 10. Limitações conhecidas

### Limitações técnicas
- diagramas de baixa resolução reduzem qualidade da extração
- diagramas muito densos podem gerar extração incompleta
- setas e conectores pequenos podem ser ignorados pelo modelo
- siglas sem contexto podem ser classificadas incorretamente

### Limitações de escopo
- o MVP não substitui arquiteto humano
- os riscos são indícios, não diagnóstico final
- as recomendações são básicas
- a análise depende da qualidade visual do diagrama
- o catálogo de regras de risco é limitado (5 regras no MVP)

---

## 11. Ordem de implementação

| Ordem | Pipeline | Motivo |
|---|---|---|
| 1 | P1 — Extração | é o coração do sistema; define a qualidade de tudo que vem depois |
| 2 | P2 — Análise de riscos | depende do JSON da P1; regras simples, implementação rápida |
| 3 | P3 — Geração do relatório | depende do JSON enriquecido da P2; é a entrega visível |
| 4 | P4 — Validação | última etapa; garante qualidade mínima antes de entregar |

---

## 12. Testes

### Estratégia
Cada pipeline é testável isoladamente porque tem entrada e saída bem definidas.

### Testes por pipeline

**P1 — Extração**
- dado um diagrama de teste com componentes conhecidos, o JSON extraído contém os componentes esperados
- dado um PDF exportado, a rota de PDF exportado é seguida (texto extraído programaticamente)
- dado um PDF escaneado, a rota de imagem é seguida (conversão para imagem)
- dado um arquivo com extensão inválida, retorna erro com motivo

**P2 — Análise de riscos**
- dado um JSON com um único banco atendendo 5 serviços, detecta risco "banco centralizado"
- dado um JSON com componente gateway sem réplica e muitas conexões, detecta "ponto único de falha"
- dado um JSON sem riscos aparentes, retorna lista vazia de riscos
- dado um JSON sem campo `components`, retorna erro

**P3 — Geração do relatório**
- dado um JSON enriquecido, o relatório gerado contém todas as 7 seções
- dado um JSON com 2 riscos, o relatório menciona ambos
- dado um JSON com `uncertainties`, o relatório inclui isso na seção de limitações

**P4 — Validação**
- dado um relatório completo e JSON consistente, a validação aprova
- dado um relatório sem seção "Recomendações", a validação rejeita com motivo
- dado um relatório que menciona componente inexistente no JSON, a validação rejeita
- dado um relatório que omite um risco presente no JSON, a validação rejeita

---

## 13. Avaliação básica da IA

Para atender ao requisito de avaliação:

1. montar conjunto pequeno de diagramas de teste (3-5 diagramas variados)
2. executar pipeline ponta a ponta em cada um
3. comparar componentes extraídos vs. componentes reais do diagrama
4. verificar se riscos detectados fazem sentido
5. avaliar se o relatório é coerente com os dados extraídos
6. documentar acertos, erros e limitações encontradas
