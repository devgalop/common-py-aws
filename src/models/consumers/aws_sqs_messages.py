from abc import ABC, abstractmethod


class SqsMessage(ABC):
    """Represents a generic SQS message.
    Args:
        ABC (_type_): Abstract base class for SQS messages.
    """

    @abstractmethod
    def serialize(self) -> str:
        """Generate string representation of the message.

        Returns:
            str: The serialized string representation of the message.
        """
        pass


class SqsMessageReceived:
    """Represents a received SQS message.

    Args:
        message_id (str): The unique identifier of the message.
        body (str): The content of the message.
        receipt_handle (str): The receipt handle associated with the message.
        retry_count (int, optional): The number of times the message has been retried. Defaults to 0.
    """
    def __init__(
        self, 
        message_id: str, 
        body: str, 
        receipt_handle: str, 
        retry_count: int = 0
    ):
        self.message_id = message_id
        self.body = body
        self.receipt_handle = receipt_handle
        self.retry_count = retry_count
