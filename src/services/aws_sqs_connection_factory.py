from typing import Any
import boto3
from ..models.aws_sqs_client import SqsConnectionRequest


class SqsConnection:
    """Represents a connection to an SQS service."""
    def __init__(self, client: Any):
        self.client = client


class SqsConnectionFactoryService:
    """Factory service for creating SQS connections.

    Args:
        connection_request (SqsConnectionRequest): The request object containing connection details.
    """
    def __init__(self, connection_request: SqsConnectionRequest):
        self.connection_request = connection_request

    def create_connection(self) -> SqsConnection:
        """Creates and returns a new SQS connection.

        Returns:
            SqsConnection: The newly created SQS connection.
        """
        client: Any = boto3.client(
            service_name="sqs",
            endpoint_url=self.connection_request.endpoint_url,
            aws_access_key_id=self.connection_request.access_key,
            aws_secret_access_key=self.connection_request.secret_key,
            region_name=self.connection_request.region,
        )
        return SqsConnection(client=client)
