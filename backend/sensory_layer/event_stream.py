import asyncio
import json
import pika
from typing import Dict, Any
from .event_encoder import UnifiedEvent

class RabbitMQEventStream:
    """
    Real-time event streaming using RabbitMQ.
    Publishes unified events to a centralized message queue for distributed processing.
    """
    def __init__(self, host: str = "localhost", port: int = 5672, exchange: str = "bizit_events"):
        self.host = host
        self.port = port
        self.exchange = exchange
        self.connection = None
        self.channel = None
    
    def connect(self):
        """Establish connection to RabbitMQ broker."""
        try:
            credentials = pika.PlainCredentials('guest', 'guest')
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange for event routing
            self.channel.exchange_declare(
                exchange=self.exchange,
                exchange_type='topic',
                durable=True
            )
            print(f"[STREAM] Connected to RabbitMQ at {self.host}:{self.port}")
            
        except Exception as e:
            print(f"[STREAM] RabbitMQ connection failed: {e}. Using in-memory fallback.")
            self.connection = None
    
    def publish_event(self, event: UnifiedEvent):
        """Publish event to RabbitMQ exchange."""
        if not self.connection:
            print(f"[STREAM] Fallback: Event {event.id} processed in-memory")
            return
        
        try:
            routing_key = f"{event.source}.{event.event_type}"
            message = event.model_dump_json()
            
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    priority=event.priority
                )
            )
            print(f"[STREAM] Published: {routing_key}")
            
        except Exception as e:
            print(f"[STREAM] Publish error: {e}")
    
    def close(self):
        """Close RabbitMQ connection."""
        if self.connection:
            self.connection.close()
            print("[STREAM] RabbitMQ connection closed")
