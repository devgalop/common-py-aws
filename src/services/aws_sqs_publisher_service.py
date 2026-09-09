from ..contracts.publisher_service import (
    PublisherService,
    PublishMessageRequest,
    PublishMessageResponse,
)
from .aws_sqs_connection_factory import SqsConnection


class SqsPublisherService(PublisherService):
    """SQS publisher service implementing the PublisherService contract.

    Args:
        sqs_client (SqsConnection): The SQS connection to use for publishing.
    """

    def __init__(self, sqs_client: SqsConnection):
        self.sqs_client = sqs_client

    async def publish(self, request: PublishMessageRequest) -> PublishMessageResponse:
        """Publish a message to the specified SQS queue.

        Args:
            request (PublishMessageRequest): The request containing the queue URL and message.

        Returns:
            PublishMessageResponse: The result of the publish operation.
        """
        try:
            response = self.sqs_client.client.send_message(
                QueueUrl=request.get_url(), MessageBody=request.get_message()
            )
            if response.get("ResponseMetadata", {}).get("HTTPStatusCode") != 200:
                return PublishMessageResponse(
                    success=False, message="Unexpected HTTP status code"
                )

            return PublishMessageResponse(
                success=True, message="Message published successfully"
            )
        except Exception as e:
            return PublishMessageResponse(success=False, message=str(e))
