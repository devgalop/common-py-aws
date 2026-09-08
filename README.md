# common-py-aws

A thin typed wrapper around AWS SQS for Python. Send and receive messages from SQS queues with async publish and a long-polling consumer.

## Features

- **Typed interfaces** — Pydantic-free, explicit dataclass-style models
- **Async publish** — `SqsPublisherService.publish()` returns `PublishMessageResponse`
- **Long-polling consumer** — Configurable `WaitTimeSeconds` for cost-efficient polling
- **Handler pattern** — Implement `ConsumerHandler` to define message processing logic
- **Idempotent queue creation** — `SqsCreatorService.create_queue()` returns existing queue if present

## Installation

```bash
# Development (editable install with pythonpath support)
pip install -e .

# Production (once packaged)
pip install common-py-aws
```

**Requirements:** Python >= 3.9, boto3 >= 1.28.0

## Quick Start

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

# 1. Connect
request = SqsConnectionRequest(
    endpoint_url="https://sqs.us-east-1.amazonaws.com",
    access_key="YOUR_ACCESS_KEY",
    secret_key="YOUR_SECRET_KEY",
    region="us-east-1",
)
connection = SqsConnectionFactoryService(request).create_connection()

# 2. Create queue (idempotent)
queue = SqsCreatorService(connection).create_queue("my-queue")

# 3. Publish async message
async def send_message():
    publisher = SqsPublisherService(connection)
    response = await publisher.publish(
        SqsPublishMessageRequest(queue_url=queue.queue_url, message="hello")
    )
    print(response.success, response.message)

asyncio.run(send_message())

# 4. Consume messages
class MyHandler(ConsumerHandler):
    async def process_message(self, message: SqsMessageReceived) -> bool:
        print(f"Received: {message.body}")
        return True  # True = delete message, False = leave it

config = SqsConsumerConfig(
    queue_url=queue.queue_url,
    max_messages=10,
    wait_time_seconds=20,
    is_enabled=True,
)
consumer = SqsConsumerService(connection, config, MyHandler())
consumer.start_consumer()
```

## Architecture

```
models/          # Data structures (SqsConnectionRequest, SqsQueue, etc.)
contracts/       # Abstract interfaces (PublisherService, ConsumerHandler)
services/        # Concrete implementations (SqsPublisherService, etc.)
```

## Configuration Reference

| Model | Key Fields |
|-------|------------|
| `SqsConnectionRequest` | `endpoint_url`, `access_key`, `secret_key`, `region` |
| `SqsConsumerConfig` | `queue_url`, `max_messages`, `wait_time_seconds`, `is_enabled` |

## Important Behaviors

| Behavior | Detail |
|----------|--------|
| `is_enabled=False` | Consumer sleeps 30s and re-checks; it does not pause |
| `process_message` returns `True` | Message is deleted from queue |
| `process_message` returns `False` | Message stays in queue for next poll |
| Exception in handler | Printed to stdout; loop continues |
| `create_queue` | Idempotent — returns existing queue if already present |
| Credentials | Explicit only; no IAM role / profile / env-var support yet |

## License

MIT
