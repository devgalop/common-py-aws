class SqsPublishMessageRequest:
    """Represents a request to publish a message to an SQS queue.
    
    Attributes:
        queue_url (str): The URL of the SQS queue.
        message (str): The message to be published.
    """
    def __init__(self, queue_url: str, message: str):
        self.queue_url = queue_url
        self.message = message