class SqsConsumerConfig:
    """Represents the configuration for an SQS consumer.

    Args:
        queue_url (str): The URL of the SQS queue to consume messages from.
        max_messages (int, optional): The maximum number of messages to retrieve per request. Defaults to 10.
        wait_time_seconds (int, optional): The duration (in seconds) for which the call waits for a message to arrive in the queue before returning. Defaults to 20.
        is_enabled (bool, optional): Indicates whether the consumer is enabled. Defaults to False.
    """
    def __init__(
        self,
        queue_url: str,
        max_messages: int = 10,
        wait_time_seconds: int = 20,
        is_enabled: bool = False,
    ):
        self.queue_url = queue_url
        self.max_messages = max_messages
        self.wait_time_seconds = wait_time_seconds
        self.is_enabled = is_enabled
