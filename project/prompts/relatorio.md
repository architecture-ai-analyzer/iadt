Você é um arquiteto de software sênior. Gere um relatório técnico de análise de arquitetura com base nos dados estruturados abaixo.

DADOS DE ENTRADA (JSON):
{enriched_json}

REGRAS OBRIGATÓRIAS:
- Use SOMENTE os dados do JSON acima. Não invente componentes, riscos ou recomendações não presentes nos dados.
- O relatório deve conter EXATAMENTE as 7 seções abaixo, com os headers exatos.
- Todos os riscos do JSON devem aparecer na seção 4.
- Todos os componentes do JSON devem aparecer na seção 2.
- A seção 6 (Limitações) deve estar presente mesmo que a análise pareça completa.

FORMATO OBRIGATÓRIO:

# Relatório de Análise de Arquitetura

## 1. Resumo executivo
[síntese em 2-4 parágrafos da arquitetura e principais achados]

## 2. Componentes identificados
[lista de todos os componentes com nome, tipo e descrição funcional]

## 3. Relações observadas
[descrição das conexões entre componentes]

## 4. Riscos arquiteturais
[cada risco com: nome, severidade, componentes afetados, evidência e impacto potencial]

## 5. Recomendações
[sugestões práticas e específicas para mitigar cada risco identificado]

## 6. Limitações da análise
[o que o sistema não conseguiu determinar; inclua as uncertainties do JSON]

## 7. Nível de confiança
[avaliação geral: alta/média/baixa, com justificativa baseada nas uncertainties e qualidade dos dados]
