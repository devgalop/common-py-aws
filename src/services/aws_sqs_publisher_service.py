from services.aws_sqs_connection_factory import (
    SqsConnection,
)
from models.publisher.aws_sqs_publish_request import SqsPublishMessageRequest

class SqsPublisherService:
    def __init__(self, sqs_client: SqsConnection):
        self.sqs_client = sqs_client

    def publish(self, request: SqsPublishMessageRequest) -> bool:
        """Publish a message to the specified SQS queue.

        Args:
            request (SqsPublishMessageRequest): The request containing the queue URL and message.

        Returns:
            bool: The result of the publish operation.
        """

        response = self.sqs_client.client.send_message(
            QueueUrl=request.queue_url, MessageBody=request.message
        )
        if response.get("ResponseMetadata", {}).get("HTTPStatusCode") != 200:
            return False

        return True

