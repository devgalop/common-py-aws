class SqsPublishMessageRequest:
    """Represents a request to publish a message to an SQS queue.
    
    Attributes:
        queue_url (str): The URL of the SQS queue.
        message (str): The message to be published.
    """
    def __init__(self, queue_url: str, message: str):
        self.queue_url = queue_url
        self.message = message

    def get_url(self) -> str:
        """Retrieve the URL of the queue to which the message will be published.

        Returns:
            str: The URL of the queue.
        """
        return self.queue_url

    def get_message(self) -> str:
        """Retrieve the message to be published.

        Returns:
            str: The message to be published.
        """
        return self.message
