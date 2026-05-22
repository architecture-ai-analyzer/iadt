# Fetch existing SQS queues
# Input: upload-queue (tasks from upload-service)
# Output: report-generation-queue (analysis results)

data "aws_sqs_queue" "input_queue" {
  name = "upload-queue"
}

data "aws_sqs_queue" "output_queue" {
  name = "report-generation-queue"
}

# Then use in configmap:
# IADT_INPUT_QUEUE_URL  = data.aws_sqs_queue.input_queue.url
# IADT_OUTPUT_QUEUE_URL = data.aws_sqs_queue.output_queue.url

