Você é um arquiteto de software sênior. Gere um relatório técnico de análise de arquitetura com base nos dados estruturados abaixo.

PADRÃO ARQUITETURAL: {pattern_type} — {pattern_description}
INTENÇÃO DO DIAGRAMA: {intent_summary} (tipo: {intent_kind})

COMPONENTES E RELAÇÕES (canonical):
{canonical_json}

OBSERVAÇÕES FACTUAIS:
{observations_json}

INFERENCES (hipóteses interpretativas com base nas observações):
{inferences_json}

CONCERNS (preocupações arquiteturais derivadas das inferences):
{concerns_json}

LIMITAÇÕES DA ANÁLISE:
{limitations_json}

REGRAS OBRIGATÓRIAS:
- Não invente componentes ou elementos visuais ausentes do diagrama — mantenha-se fiel ao canonical.
- É permitido e esperado inferir preocupações arquiteturais além do que está explícito nos dados, desde que: (a) estejam fundamentadas nos padrões estruturais observados, (b) sejam identificadas como inferência, e (c) sejam coerentes com o padrão arquitetural identificado. Problemas como acoplamento, duplicação de fluxo, SPOF e latência raramente aparecem explícitos num diagrama — são sempre inferidos.
- O relatório deve conter EXATAMENTE as 7 seções abaixo, com os headers exatos.
- Todos os concerns do JSON devem aparecer na seção 4.
- Todos os componentes do JSON devem aparecer na seção 2.
- A seção 4 deve articular o raciocínio: para cada concern, explique a observação que o fundamenta, a inference que o originou, e a implicação prática.
- A seção 6 deve listar as limitations do JSON e as uncertainties do canonical.
- A seção 7 deve avaliar a confiança com base nas limitations e na confiança das inferences.

FORMATO OBRIGATÓRIO:

# Relatório de Análise de Arquitetura

## 1. Resumo executivo
[síntese em 2-4 parágrafos da arquitetura e principais achados; mencione o tipo de diagrama e o que ele comunica]

## 2. Componentes identificados
[lista de todos os componentes com nome, tipo e descrição funcional]

## 3. Relações observadas
[descrição das conexões entre componentes]

## 4. Riscos arquiteturais
[para cada concern: título, severidade, componentes afetados, e raciocínio encadeado — "observei X, inferi Y, portanto me preocupo com Z"]

## 5. Recomendações
[sugestões práticas e específicas para mitigar cada concern identificado]

## 6. Limitações da análise
[liste as limitations do JSON e as uncertainties do canonical; o que não foi possível determinar e por quê]

## 7. Nível de confiança
[avaliação geral: alta/média/baixa, com justificativa baseada nas limitations e na confiança das inferences]
