# IADT — Análise de Diagramas de Arquitetura

Pipeline de IA que recebe um diagrama de arquitetura (imagem ou PDF) e gera automaticamente um relatório técnico com componentes identificados, riscos arquiteturais e recomendações.

## Pré-requisitos

- Python 3.11+
- Chave de API do provedor LLM escolhido (Anthropic ou OpenAI)

## Instalação

```bash
cd project
winget install -e --id Python.Python.3.13
pip install -e ".[dev]"
```

## Configuração

Crie um arquivo `.env` dentro da pasta `project/` com base no provedor desejado:

**Anthropic (Claude)**
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sua-chave-aqui
```

**OpenAI**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sua-chave-aqui
```

## Como usar

```bash
cd project
python cli.py <caminho-do-diagrama>
```

**Exemplos:**
```bash
# Imagem
python cli.py samples/image_1.jpg

# PDF
python cli.py diagrama.pdf

# Definindo pasta de saída
python cli.py samples/image_1.jpg --output meu_relatorio/
```

**Formatos suportados:** `.png`, `.jpg`, `.jpeg`, `.pdf`

## Saída gerada

Para cada execução, os artefatos são salvos em `runs/<nome-do-arquivo>/`:

| Arquivo | Descrição |
|---|---|
| `canonical.json` | Componentes e relações extraídos do diagrama |
| `enriched.json` | Canonical + riscos arquiteturais identificados |
| `report.md` | Relatório técnico final em Markdown |

O terminal exibe o resultado da validação e o tempo de execução:
```
Validação: APROVADO
Tempo total: 12.4s

Artefatos gerados:
  canonical: runs/image_1/canonical.json
  enriched:  runs/image_1/enriched.json
  report:    runs/image_1/report.md
```

## Testes

```bash
cd project
pytest
```
