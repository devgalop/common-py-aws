from typing import Any
import json
from ..models.consumers.aws_sqs_redrive_policy import SqsRedrivePolicy
from ..models.consumers.aws_sqs_queue import SqsQueue, SqsQueueAttributes
from .aws_sqs_connection_factory import SqsConnection


class SqsCreatorService:
    def __init__(self, client: SqsConnection):
        self.sqs_client: Any = client.client

    def create_queue(
        self, queue_name: str, redrive_policy: SqsRedrivePolicy | None = None
    ) -> SqsQueue:
        existing_queue = self.validate_queue_exists(queue_name)
        if existing_queue:
            return existing_queue
        queue_url: str = ""
        if redrive_policy:
            response = self.sqs_client.create_queue(
                QueueName=queue_name, Attributes=json.dumps(redrive_policy.to_dict())
            )
            queue_url = response["QueueUrl"]
        else:
            response = self.sqs_client.create_queue(QueueName=queue_name)
            queue_url = response["QueueUrl"]
        return SqsQueue(name=queue_name, queue_url=queue_url)

    def get_queue_attributes(self, queue_url: str) -> SqsQueueAttributes:
        response = self.sqs_client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=[
                "QueueArn",
                "ApproximateNumberOfMessages",
                "ApproximateNumberOfMessagesNotVisible",
            ],
        )["Attributes"]
        return SqsQueueAttributes(
            queue_arn=response["QueueArn"],
            aprox_number_of_messages=int(response["ApproximateNumberOfMessages"]),
            aprox_number_of_messages_in_transit=int(
                response["ApproximateNumberOfMessagesNotVisible"]
            ),
        )

    def validate_queue_exists(self, queue_name: str) -> SqsQueue | None:
        try:
            queue_url = self.sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]
            return SqsQueue(name=queue_name, queue_url=queue_url)
        except self.sqs_client.exceptions.QueueDoesNotExist:
            return None
