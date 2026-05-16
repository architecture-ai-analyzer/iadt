# IADT Worker - Dockerfile

## 📦 Build da Imagem

### Pré-requisitos
- Docker instalado
- Acesso a um registry (Docker Hub, ECR, etc)

### Build Local

```bash
cd e:/code/iadt

# Build simples
docker build -t iadt-worker:latest .

# Build com tag de versão
docker build -t iadt-worker:v1.0.0 .
```

### Push para Registry

#### **Docker Hub**

```bash
# Login
docker login

# Tag
docker tag iadt-worker:latest seu-usuario/iadt-worker:latest

# Push
docker push seu-usuario/iadt-worker:latest

# Usar no Terraform
# terraform.tfvars:
# iadt_image = "seu-usuario/iadt-worker:latest"
```

#### **AWS ECR**

```bash
# Create repository
aws ecr create-repository \
  --repository-name iadt-worker \
  --region us-east-2

# Get login token
aws ecr get-login-password --region us-east-2 | \
  docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-2.amazonaws.com

# Tag
docker tag iadt-worker:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-2.amazonaws.com/iadt-worker:latest

# Push
docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-2.amazonaws.com/iadt-worker:latest

# Usar no Terraform
# terraform.tfvars:
# iadt_image = "<AWS_ACCOUNT_ID>.dkr.ecr.us-east-2.amazonaws.com/iadt-worker:latest"
```

#### **Outras Opções (GitHub Container Registry, GitLab, etc)**

```bash
# GitHub Container Registry
docker tag iadt-worker:latest ghcr.io/seu-usuario/iadt-worker:latest
docker push ghcr.io/seu-usuario/iadt-worker:latest
```

---

## 🏗️ Estrutura do Dockerfile

### Multi-stage build

1. **Builder Stage**: Compila dependências Python (com build-tools)
2. **Runtime Stage**: Imagem final mínima (apenas runtime necessário)

### Otimizações

- ✅ Usa Python 3.11-slim (pequeno)
- ✅ Instala apenas dependências runtime (sem build-tools)
- ✅ Virtual env isolado
- ✅ User não-root (segurança)
- ✅ PYTHONUNBUFFERED=1 (logs imediatos)
- ✅ Health check configurado
- ✅ .dockerignore para evitar arquivos desnecessários

### Dependências Incluídas

```
anthropic>=0.40.0        # LLM - Anthropic
openai>=1.0.0           # LLM - OpenAI
pymupdf>=1.24.0         # PDF parsing
pdf2image>=1.17.0       # PDF to image
jsonschema>=4.23.0      # JSON validation
python-dotenv>=1.0.0    # Environment variables
Pillow>=10.0.0          # Image processing
boto3>=1.35.0           # AWS SDK (SQS, S3)
```

---

## 🧪 Testar Localmente

### Build
```bash
docker build -t iadt-worker:latest .
```

### Rodar com variáveis de teste
```bash
docker run \
  -e IADT_INPUT_QUEUE_URL="https://sqs.us-east-2.amazonaws.com/..." \
  -e IADT_OUTPUT_QUEUE_URL="https://sqs.us-east-2.amazonaws.com/..." \
  -e AWS_REGION="us-east-2" \
  -e LLM_PROVIDER="openai" \
  -e OPENAI_API_KEY="sk-..." \
  iadt-worker:latest
```

### Ver logs
```bash
docker logs <container-id>
```

---

## 📝 Variáveis de Ambiente

Configuradas via Terraform ConfigMap:

```bash
# AWS
AWS_REGION=us-east-2
CLOUD_AWS_REGION=us-east-2

# SQS
IADT_INPUT_QUEUE_URL=https://sqs.us-east-2.amazonaws.com/...
IADT_OUTPUT_QUEUE_URL=https://sqs.us-east-2.amazonaws.com/...
IADT_WORKER_VISIBILITY_TIMEOUT=300

# S3
S3_BUCKET=upload-service-bucket-ai-analyzer
S3_REGION=us-east-2

# LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL_TEXT=gpt-4o-mini
OPENAI_MODEL_VISION=gpt-4o
ANTHROPIC_API_KEY=sk-... (fallback)

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
PYTHONUNBUFFERED=1
```

---

## 📊 Tamanho da Imagem

Esperado: **~300-400MB** (multi-stage otimizado)

---

## 🔒 Segurança

- ✅ User não-root (iadt)
- ✅ Imagem slim (menos superfície de ataque)
- ✅ PYTHONDONTWRITEBYTECODE=1 (sem .pyc files)
- ✅ Health check para detectar problemas

---

## 🚀 Deploy via Terraform

Após push para registry, atualizar `terraform/envs/dev/terraform.tfvars`:

```hcl
iadt_image = "seu-registry/iadt-worker:v1.0.0"
```

Depois:
```bash
cd terraform/envs/dev
terraform apply -var-file=terraform.tfvars
```

---

## ❓ Troubleshooting

### "ImportError: No module named 'worker'"
- Verificar se `worker.py` está no COPY
- Verificar se entrypoint é correto: `python -m worker`

### "ModuleNotFoundError: No module named 'adapters'"
- Verificar se `/app` tem todas as pastas do projeto
- Executar `docker build --no-cache` para rebuild completo

### Container fica em loop/crash
- Ver logs: `docker logs <id>`
- Verificar variáveis de ambiente (SQS URLs, credentials)
- Testar localmente: `python -m worker`
