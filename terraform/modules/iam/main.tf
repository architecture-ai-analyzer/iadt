# Extract OIDC provider ID from URL
locals {
  oidc_provider_id = regex("[^/]+$", var.oidc_provider_url)
}

# IAM Role for IRSA (IAM Roles for Service Accounts)
resource "aws_iam_role" "iadt_worker" {
  name = "${var.project_name}-irsa-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = var.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${var.oidc_provider_url}:sub" = "system:serviceaccount:${var.kubernetes_namespace}:${var.kubernetes_service_account}"
            "${var.oidc_provider_url}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Policy for SQS - Receive messages from input queue
resource "aws_iam_role_policy" "sqs_input_receive" {
  name = "${var.project_name}-sqs-input-receive-${var.environment}"
  role = aws_iam_role.iadt_worker.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:ChangeMessageVisibility"
        ]
        Resource = var.input_queue_arn
      }
    ]
  })
}

# Policy for SQS - Send messages to output queue
resource "aws_iam_role_policy" "sqs_output_send" {
  name = "${var.project_name}-sqs-output-send-${var.environment}"
  role = aws_iam_role.iadt_worker.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = var.output_queue_arn
      }
    ]
  })
}

# Policy for S3 - Read diagrams
resource "aws_iam_role_policy" "s3_read" {
  name = "${var.project_name}-s3-read-${var.environment}"
  role = aws_iam_role.iadt_worker.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:ListBucket"
        ]
        Resource = [
          var.s3_bucket_arn,
          "${var.s3_bucket_arn}/*"
        ]
      }
    ]
  })
}

# Kubernetes service account annotation
resource "kubernetes_service_account" "iadt_worker" {
  metadata {
    name      = var.kubernetes_service_account
    namespace = var.kubernetes_namespace
    annotations = {
      "eks.amazonaws.com/role-arn" = aws_iam_role.iadt_worker.arn
    }
  }

  automount_service_account_token = true
}
