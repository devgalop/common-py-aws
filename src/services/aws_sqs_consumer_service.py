import asyncio
from abc import ABC
from ..contracts.consumer_handler import ConsumerHandler
from ..models.consumers.aws_sqs_consumer_config import SqsConsumerConfig
from ..models.consumers.aws_sqs_messages import SqsMessageReceived
from .aws_sqs_connection_factory import SqsConnection


class SqsConsumerService(ABC):
    """Represents an abstract SQS consumer service.
    This class provides the basic structure and functionality for consuming messages from an SQS queue.
    Subclasses must implement the `process_message` method to define custom message processing logic.

    Args:
        ABC (_type_): The abstract base class for the consumer service.
    """

    def __init__(
        self,
        sqs_client: SqsConnection,
        sqs_config: SqsConsumerConfig,
        sqs_handler: ConsumerHandler,
    ):
        self.sqs_client = sqs_client
        self.sqs_config = sqs_config
        self.sqs_handler = sqs_handler
        self._task: asyncio.Task | None = None
        self._stopping = False

    def start_consumer(self):
        """Starts the SQS consumer service.

        This method sets the stopping flag to False and creates an asynchronous task to consume messages from the SQS queue.
        """
        self._stopping = False
        self._task = asyncio.create_task(self._consume_messages())

    async def _consume_messages(self):
        """Consumes messages from the SQS queue in a loop until the stopping flag is set."""
        while not self._stopping:
            if not self.sqs_config.is_enabled:
                await asyncio.sleep(30)
                continue

            try:
                messages = await asyncio.to_thread(
                    self.sqs_client.client.receive_message,
                    QueueUrl=self.sqs_config.queue_url,
                    MaxNumberOfMessages=self.sqs_config.max_messages,
                    WaitTimeSeconds=self.sqs_config.wait_time_seconds,
                    AttributeNames=["ApproximateReceiveCount"],
                )
                if not messages or "Messages" not in messages:
                    await asyncio.sleep(30)
                    continue

                for message in messages.get("Messages", []):
                    message_recieved = SqsMessageReceived(
                        message_id=message["MessageId"],
                        body=message["Body"],
                        receipt_handle=message["ReceiptHandle"],
                        retry_count=int(
                            message["Attributes"].get("ApproximateReceiveCount", 0)
                        ),
                    )
                    result = await self.sqs_handler.process_message(message_recieved)
                    if (
                        not result
                        and message_recieved.retry_count >= self.sqs_config.max_retries
                    ):
                        # Send message to DLQ if configured
                        if self.sqs_config.dlq_url is not None:
                            await asyncio.to_thread(
                                self.sqs_client.client.send_message,
                                QueueUrl=self.sqs_config.dlq_url,
                                MessageBody=message_recieved.body,
                            )
                        # Delete the message from the main queue after exceeding max retries
                        await asyncio.to_thread(
                            self.sqs_client.client.delete_message,
                            QueueUrl=self.sqs_config.queue_url,
                            ReceiptHandle=message_recieved.receipt_handle,
                        )
                    if result:
                        await asyncio.to_thread(
                            self.sqs_client.client.delete_message,
                            QueueUrl=self.sqs_config.queue_url,
                            ReceiptHandle=message_recieved.receipt_handle,
                        )
            except Exception as e:
                print(f"Error processing messages: {e}")
            await asyncio.sleep(30)

    async def stop_consumer(self):
        """Stops the SQS consumer service.

        This method sets the stopping flag to True, cancels the asynchronous task consuming messages,
        and waits for the task to complete.
        """
        self._stopping = True
        if self._task is not None:
            self._task.cancel()
        try:
            if self._task is not None:
                await self._task
        except asyncio.CancelledError:
            pass
