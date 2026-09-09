class SqsRedrivePolicy:
    """Represents the redrive policy of an SQS queue.

    Args:
        dead_letter_target_arn (str): The ARN of the dead-letter queue.
        max_receive_count (int): The maximum number of times a message can be received before being sent to the dead-letter queue.
    """

    def __init__(self, dead_letter_target_arn: str, max_receive_count: int):
        self.dead_letter_target_arn = dead_letter_target_arn
        self.max_receive_count = max_receive_count

    def to_dict(self) -> dict[str, str | int]:
        return {
            "deadLetterTargetArn": self.dead_letter_target_arn,
            "maxReceiveCount": self.max_receive_count,
        }
