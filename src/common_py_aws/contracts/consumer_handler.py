from abc import ABC, abstractmethod
from ..models.consumers.aws_sqs_messages import SqsMessageReceived


class ConsumerHandler(ABC):

    @abstractmethod
    async def process_message(self, message: SqsMessageReceived) -> bool:
        """Processes a single SQS message.

        Subclasses must implement this method to define custom message processing logic.

        Args:
            message (SqsMessageReceived): The received SQS message to process.

        Returns:
            bool: True if the message was successfully processed and should be deleted from the queue, False otherwise.
        """
        pass
