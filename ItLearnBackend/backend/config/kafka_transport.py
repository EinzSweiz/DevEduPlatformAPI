from kombu.transport.virtual import Channel, Transport
from kafka import KafkaProducer, KafkaConsumer

class KafkaChannel(Channel):
    def _put(self, queue, message, **kwargs):
        producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            linger_ms=5,
            heartbeat_interval_ms=3000,  # Kafka heartbeat interval
        )
        try:
            producer.send(queue, value=message)
        finally:
            producer.close()

    def _get(self, queue):
        consumer = KafkaConsumer(
            queue,
            bootstrap_servers='localhost:9092',
            auto_offset_reset='earliest',
            group_id='celery',
            enable_auto_commit=True,
            session_timeout_ms=30000,  # Kafka session timeout
            heartbeat_interval_ms=3000,  # Kafka heartbeat interval
        )
        for message in consumer:
            return message.value
   
class KafkaTransport(Transport):
    Channel = KafkaChannel
    default_port = 9092
    driver_type = 'kafka'
    driver_name = 'kafka'