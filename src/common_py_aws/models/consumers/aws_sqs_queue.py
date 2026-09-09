class SqsQueue:
    """Represents an SQS queue.

    Args:
        name (str): The name of the SQS queue.
        queue_url (str): The URL of the SQS queue.
    """

    def __init__(self, name: str, queue_url: str):
        self.name = name
        self.queue_url = queue_url


class SqsQueueAttributes:
    """Represents the attributes of an SQS queue.

    Args:
        attributes (dict[str, Any]): The attributes of the SQS queue.
    """

    def __init__(
        self,
        queue_arn: str,
        aprox_number_of_messages: int,
        aprox_number_of_messages_in_transit: int,
    ):
        self.queue_arn = queue_arn
        self.aprox_number_of_messages = aprox_number_of_messages
        self.aprox_number_of_messages_in_transit = aprox_number_of_messages_in_transit
