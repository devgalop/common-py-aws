# User Guide — common-py-aws

A thin typed wrapper around AWS SQS for Python. This guide walks from setup to production use.

---

## Prerequisites

- Python >= 3.9
- AWS account with SQS permissions
- AWS access key and secret key (no IAM role / profile / env-var support yet)

---

## Installation

```bash
pip install -e .       # editable dev install
pip install common-py-aws  # when packaged
```

Requires: `boto3 >= 1.28.0`

---

## Connection Setup

Create a connection using explicit credentials:

```python
from common_py_aws import SqsConnectionRequest, SqsConnectionFactoryService

request = SqsConnectionRequest(
    endpoint_url="https://sqs.us-east-1.amazonaws.com",
    access_key="YOUR_ACCESS_KEY",
    secret_key="YOUR_SECRET_KEY",
    region="us-east-1",
)
connection = SqsConnectionFactoryService(request).create_connection()
```

`connection` is a `SqsConnection` wrapping a boto3 SQS client.

---

## Creating a Queue

```python
from common_py_aws import SqsCreatorService

queue = SqsCreatorService(connection).create_queue("my-queue")
print(queue.queue_url)   # Use this for publishing/consuming
print(queue.name)        # "my-queue"
```

`create_queue` is **idempotent** — if the queue already exists, it returns the existing queue without error.

---

## Publishing Messages

```python
import asyncio
from common_py_aws import SqsPublisherService, SqsPublishMessageRequest

async def publish():
    publisher = SqsPublisherService(connection)
    response = await publisher.publish(
        SqsPublishMessageRequest(queue_url=queue.queue_url, message="hello world")
    )
    print(response.success)   # True or False
    print(response.message)   # "Message published successfully" or error string

asyncio.run(publish())
```

**Return type:** `PublishMessageResponse(success: bool, message: str)`

---

## Consuming Messages

### Step 1 — Implement a Handler

```python
from common_py_aws import ConsumerHandler, SqsMessageReceived

class MyHandler(ConsumerHandler):
    async def process_message(self, message: SqsMessageReceived) -> bool:
        print(f"Message {message.message_id}: {message.body}")
        # Return True to delete the message, False to leave it in the queue
        return True
```

### Step 2 — Configure and Start

```python
from common_py_aws import SqsConsumerService, SqsConsumerConfig

config = SqsConsumerConfig(
    queue_url=queue.queue_url,
    max_messages=10,          # Max messages per receive call
    wait_time_seconds=20,     # Long polling duration (0–20)
    is_enabled=True,          # False = consumer sleeps 30s per cycle
)
consumer = SqsConsumerService(connection, config, MyHandler())
consumer.start_consumer()
```

### Step 3 — Stop Gracefully

```python
await consumer.stop_consumer()
```

---

## SqsConsumerConfig Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `queue_url` | `str` | — | Required. URL of the queue to consume from. |
| `max_messages` | `int` | `10` | Max messages per `receive_message` call (1–10). |
| `wait_time_seconds` | `int` | `20` | Long polling wait time (0–20). |
| `is_enabled` | `bool` | `False` | When `False`, consumer sleeps 30s then re-checks. Does not pause/resume. |

---

## ConsumerHandler Return Semantics

| Return | Behavior |
|--------|----------|
| `True` | Message is deleted from the queue via `delete_message`. |
| `False` | Message stays in the queue and will be redelivered on next poll. |

---

## Consumer Loop Behavior

The consumer loop:

1. Checks `is_enabled`. If `False`, sleeps 30s and repeats.
2. Calls `receive_message` with `WaitTimeSeconds` (long polling).
3. If no messages, sleeps 30s and repeats.
4. For each message, calls `handler.process_message()`.
5. Deletes the message if handler returns `True`.
6. Catches **all exceptions** in the loop, prints them, and continues.

**There is no retry or dead-letter handling** — implement this in your `process_message` handler if needed.

---

## Error Handling Notes

| Scenario | Behavior |
|----------|----------|
| Publish failure | `response.success = False`, `response.message` contains error |
| Handler exception | Printed to stdout, loop continues, message NOT deleted |
| Queue not found | Raises boto3 `QueueDoesNotExist` |
| Invalid credentials | Raises boto3 authentication error |

---

## Full Example

```python
import asyncio
from common_py_aws import (
    SqsConnectionRequest,
    SqsConnectionFactoryService,
    SqsCreatorService,
    SqsPublisherService,
    SqsConsumerService,
    SqsConsumerConfig,
    ConsumerHandler,
    SqsPublishMessageRequest,
    SqsMessageReceived,
)

async def main():
    # Connect
    request = SqsConnectionRequest(
        endpoint_url="https://sqs.us-east-1.amazonaws.com",
        access_key="YOUR_KEY",
        secret_key="YOUR_SECRET",
        region="us-east-1",
    )
    connection = SqsConnectionFactoryService(request).create_connection()

    # Create queue
    queue = SqsCreatorService(connection).create_queue("my-queue")

    # Publish
    publisher = SqsPublisherService(connection)
    await publisher.publish(
        SqsPublishMessageRequest(queue_url=queue.queue_url, message="test")
    )

    # Consume
    class MyHandler(ConsumerHandler):
        async def process_message(self, message: SqsMessageReceived) -> bool:
            print(f"Got: {message.body}")
            return True

    config = SqsConsumerConfig(queue_url=queue.queue_url, is_enabled=True)
    consumer = SqsConsumerService(connection, config, MyHandler())
    consumer.start_consumer()

    # Run for 60 seconds then stop
    await asyncio.sleep(60)
    await consumer.stop_consumer()

asyncio.run(main())
```
