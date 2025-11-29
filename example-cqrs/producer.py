# producer.py
import json
import time
import pika
from models import Session, UserWrite, init_db

# RabbitMQ connection
RABBIT_URL = "amqp://guest:guest@localhost:5672/"
QUEUE = "user_events"

# Ensure tables exist
init_db()

def publish_event(ev: dict):
    params = pika.URLParameters(RABBIT_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.basic_publish(
        exchange="",
        routing_key=QUEUE,
        body=json.dumps(ev).encode("utf-8"),
        properties=pika.BasicProperties(delivery_mode=2)  # persistent messages
    )
    conn.close()
    print("Published event:", ev)

def create_user(username: str, email: str):
    s = Session()
    try:
        user = UserWrite(username=username, email=email)
        s.add(user)
        s.commit()           # commit transaction (write model)
        s.refresh(user)      # get generated id
        # publish event after successful commit
        ev = {"type": "UserCreated", "data": {"id": user.id, "username": username, "email": email}, "ts": time.time()}
        publish_event(ev)
        return user.id
    except Exception as e:
        s.rollback()
        raise
    finally:
        s.close()

if __name__ == "__main__":
    # Simple CLI usage without framework
    import sys
    if len(sys.argv) != 3:
        print("Usage: python producer.py <username> <email>")
        print("Example: python producer.py alice alice@example.com")
        sys.exit(1)
    username, email = sys.argv[1], sys.argv[2]
    uid = create_user(username, email)
    print("Created user id:", uid)
