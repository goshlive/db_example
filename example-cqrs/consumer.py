# consumer.py
import json
import pika
from models import Session, UserView, init_db

RABBIT_URL = "amqp://guest:guest@localhost:5672/"
QUEUE = "user_events"

init_db()

def project_user_created(data):
    s = Session()
    try:
        # Idempotent upsert: use merge (SQLAlchemy) to insert-or-update by PK
        uv = UserView(id=data["id"], username=data["username"],
                      email=data["email"],
                      display_name=data["username"].capitalize())
        s.merge(uv)
        s.commit()
        print("Projected user:", data["id"])
    except Exception as e:
        s.rollback()
        print("Projection error:", e)
    finally:
        s.close()

def on_message(ch, method, properties, body):
    ev = json.loads(body.decode("utf-8"))
    evtype = ev.get("type")
    if evtype == "UserCreated":
        project_user_created(ev["data"])
    # Acknowledge so RabbitMQ removes the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    params = pika.URLParameters(RABBIT_URL)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.queue_declare(queue=QUEUE, durable=True)
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=QUEUE, on_message_callback=on_message)
    print("Consumer started; waiting for messages (CTRL+C to stop).")
    try:
        ch.start_consuming()
    except KeyboardInterrupt:
        ch.stop_consuming()
    conn.close()

if __name__ == "__main__":
    start_consumer()
