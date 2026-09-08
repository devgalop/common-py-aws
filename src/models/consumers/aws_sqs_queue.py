class SqsQueue:
    """Represents an SQS queue.

    Args:
        name (str): The name of the SQS queue.
        queue_url (str): The URL of the SQS queue.
    """
    def __init__(self, 
                 name: str, 
                 queue_url: str):
        self.name = name
        self.queue_url = queue_url
