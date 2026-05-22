# IADT - Infraestrutura Terraform

Infraestrutura como código (Terraform) para o IADT em AWS EKS. **Simplificado para projeto acadêmico + Free tier**.

## 📋 Recursos Provisionados

### AWS
- **SQS** (REFERENCIADAS - já existem):
  - `upload-queue`: recebe tarefas do upload-service
  - `report-generation-queue`: publica resultados
  - Retenção: 1 dia (Free tier friendly)
  - Sem DLQ (simplificado)

- **S3**: Referência ao bucket do upload-service

### Kubernetes (EKS)
- **Namespace**: `iadt` isolado
- **Service Account**: `iadt-worker` simples (sem IRSA)
- **Deployment**: 1-3 pods com scaling automático:
  - CPU: 250m → 500m (muito leve)
  - Memory: 256Mi → 1Gi
  - Health checks básicos
  - HPA ativo (min: 1, max: 3 replicas)

- **Service**: ClusterIP para métricas
- **ConfigMap**: Variáveis de ambiente
- **Secrets**: API keys opcionais (Anthropic/OpenAI)

## 🗂️ Estrutura

```
terraform/
├── README.md            # Esta documentação
├── providers.tf         # (Vazio - tudo em envs/dev)
├── main.tf             # (Vazio - tudo em envs/dev)
├── variables.tf        # (Vazio - tudo em envs/dev)
├── data.tf             # (Vazio - tudo em envs/dev)
├── outputs.tf          # (Vazio - tudo em envs/dev)
├── modules/            # (DEPRECATED - deixado por referência)
│   ├── sqs/
│   └── iam/
└── envs/
    └── dev/            # ⭐ AQUI! Tudo está aqui
        ├── providers.tf
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        ├── data-sqs.tf
        ├── k8s-namespace.tf
        ├── k8s-service-account.tf
        ├── k8s-configmap.tf
        ├── k8s-secret.tf
        ├── k8s-deployment.tf
        ├── k8s-hpa.tf
        ├── k8s-service.tf
        ├── api-keys.tf
        └── terraform.tfvars
```

## 🚀 Quick Start

### Pré-requisitos
- Terraform >= 1.0
- AWS CLI + kubectl configurados
- Filas SQS criadas: `upload-queue`, `report-generation-queue`
- EKS cluster disponível
- S3 bucket para state: `tf-state-ai-architecture-analyzer`

### Inicializar (SEMPRE EM DEV!)

```bash
cd envs/dev
terraform init
```

❌ **NÃO** rode `terraform init` na raiz
✅ **SEMPRE** rode em `envs/dev/`

### Aplicar

```bash
cd envs/dev
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

### Deploy

```bash
cd terraform/envs/dev

# Initialize
terraform init

# Review
terraform plan -var-file=terraform.tfvars

# Apply
terraform apply -var-file=terraform.tfvars
```

### Verificar

```bash
# Pods
kubectl get pods -n iadt

# Logs
kubectl logs -n iadt -l app=iadt-worker -f

# Filas
terraform output
```

## 🔑 Adicionar Chave de API (opcional)

```bash
# Anthropic
export TF_VAR_anthropic_api_key="sk-ant-..."
terraform apply -var-file=terraform.tfvars

# Ou via kubectl depois
kubectl create secret generic iadt-anthropic-api-key \
  --from-literal=ANTHROPIC_API_KEY="sk-ant-..." \
  -n iadt

# Reiniciar pod
kubectl rollout restart deployment/iadt-worker -n iadt
```

## ⚙️ Customização

### Mudar Docker Image

Edite `terraform/envs/dev/terraform.tfvars`:
```hcl
iadt_image = "seu-registry/seu-worker:v1.0.0"
```

### Mudar Região

```hcl
region_default = "us-east-1"
```

### Aumentar Recursos

Edite `envs/dev/variables.tf`:
```hcl
variable "iadt_cpu_request" {
  default = "500m"  # aumentar
}
```

## 🔍 Troubleshooting

### Pod não inicia?

```bash
kubectl describe pod -n iadt <pod-name>
kubectl logs -n iadt -l app=iadt-worker
```

### Erro de permissão SQS?

```bash
# Verificar role IRSA
kubectl describe sa iadt-worker -n iadt

# Testar acesso
aws sqs list-queues --region us-east-2
```

### Fila não recebe mensagens?

```bash
# Verificar URLs
terraform output

# Testar envio
aws sqs send-message \
  --queue-url <url> \
  --message-body '{"test": "message"}'
```

## 🧹 Limpeza

```bash
cd terraform/envs/dev
terraform destroy -var-file=terraform.tfvars
```

## 📚 Docs

- **QUICKSTART.md** - Setup em 3 passos
- **INTEGRATION.md** - Fluxo com upload-service
- **STRUCTURE.md** - Detalhes da arquitetura

---

**Ambiente**: Dev only (academic)  
**Free tier**: Otimizado ✓

# Produção
cd ../production
terraform init
terraform apply -var-file=terraform.tfvars
```

### 4. Configurar API Keys (Secrets)

#### Opção A: Via Terraform (variáveis de ambiente)

```bash
# Dentro do diretório do ambiente (dev, homologation ou production)

# Para Anthropic
export TF_VAR_anthropic_api_key="sk-ant-..."
terraform apply -var-file=terraform.tfvars

# Ou para OpenAI
export TF_VAR_openai_api_key="sk-..."
terraform apply -var-file=terraform.tfvars
```

#### Opção B: Via kubectl (manual)

```bash
# Criar secret para Anthropic
kubectl create secret generic iadt-anthropic-api-key \
  --from-literal=ANTHROPIC_API_KEY="sk-ant-..." \
  -n iadt

# Ou para OpenAI
kubectl create secret generic iadt-openai-api-key \
  --from-literal=OPENAI_API_KEY="sk-..." \
  -n iadt
```

### 5. Verificar deployment

```bash
# Verificar namespace foi criado
kubectl get namespaces | grep iadt

# Verificar deployment
kubectl get deployments -n iadt

# Verificar pods
kubectl get pods -n iadt

# Verificar logs
kubectl logs -n iadt -l app=iadt-worker --tail=50

# Verificar HPA status
kubectl get hpa -n iadt

# Verificar service
kubectl get svc -n iadt
```

## 📊 Variáveis por Ambiente

### Dev
- Replicas: 1
- CPU Request: 500m | Limit: 1000m
- Memory Request: 512Mi | Limit: 2Gi
- HPA: min=1, max=5, target=70%
- Visibility Timeout: 3600s (1 hora)

### Homologation
- Replicas: 2
- CPU Request: 1000m | Limit: 2000m
- Memory Request: 1Gi | Limit: 4Gi
- HPA: min=2, max=10, target=70%
- Visibility Timeout: 3600s

### Production
- Replicas: 3
- CPU Request: 1000m | Limit: 2000m
- Memory Request: 1Gi | Limit: 4Gi
- HPA: min=3, max=20, target=60%
- Visibility Timeout: 3600s

## 🔄 Fluxo de Dados

```
Upload Service
    ↓ (PUT object)
    S3 Bucket
    ↓ (publish message)
    SQS Input Queue
    ↓ (consume)
    IADT Worker Pod
    ↓ (GET S3 object + LLM analysis)
    Analysis Result
    ↓ (send message)
    SQS Output Queue
    ↓ (consume)
    Upload Service (listener)
    ↓ (update status)
    RDS Database
```

## 🛠️ Troubleshooting

### Pod não está iniciando
```bash
# Verificar eventos
kubectl describe pod -n iadt <pod-name>

# Verificar logs
kubectl logs -n iadt <pod-name>

# Verificar recursos
kubectl top pods -n iadt
```

### Erro de permissão de SQS
```bash
# Verificar role IRSA
kubectl describe sa iadt-worker -n iadt

# Verificar annotations
kubectl get sa iadt-worker -n iadt -o yaml | grep eks.amazonaws.com/role-arn
```

### HPA não está escalando
```bash
# Verificar status
kubectl get hpa -n iadt -w

# Verificar métricas
kubectl top pods -n iadt
```

### ConfigMap/Secret não foi atualizado
```bash
# Deletar pods para forçar re-leitura
kubectl rollout restart deployment/iadt-worker -n iadt
```

## 📝 Atualizações Comuns

### Alterar imagem Docker
```bash
# Atualizar terraform.tfvars
iadt_image = "your-registry/iadt-worker:v1.2.0"

# Aplicar
terraform apply -var-file=terraform.tfvars
```

### Escalar replicas
```bash
# Editar terraform.tfvars
iadt_replicas = 5

# Aplicar
terraform apply -var-file=terraform.tfvars
```

### Alterar recursos
```bash
# terraform.tfvars
iadt_cpu_request    = "2000m"
iadt_memory_request = "2Gi"

# Aplicar (vai reconverter Pods)
terraform apply -var-file=terraform.tfvars
```

## 🧹 Destruir Recursos

```bash
# CUIDADO: Isso vai deletar SQS, IAM roles, Kubernetes resources, etc.

cd terraform/envs/dev
terraform destroy -var-file=terraform.tfvars

# Confirmar digitando "yes"
```

## 📤 Outputs Úteis

Após `terraform apply`, você terá:

```bash
# Ver outputs
terraform output

# Outputs específicos
terraform output input_queue_url
terraform output output_queue_url
terraform output irsa_role_arn
```

## 🔗 Integração com Upload-Service

O IADT espera que upload-service publique mensagens em:
- `IADT_INPUT_QUEUE_URL` (veja `terraform output input_queue_url`)

E publica resultados em:
- `IADT_OUTPUT_QUEUE_URL` (veja `terraform output output_queue_url`)

Esses outputs devem ser consumidos pela configuração do upload-service.

## 📚 Referências

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Kubernetes Provider](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)
- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [IRSA Documentation](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)
