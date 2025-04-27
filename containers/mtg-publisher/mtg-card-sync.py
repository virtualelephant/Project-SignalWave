import os
import time
import pika
import logging
from mtgsdk import Card, Set
from urllib.error import HTTPError
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MTGCardPublisher")

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq.services.svc.cluster.local') 
rabbitmq_port_env = os.getenv('RABBITMQ_PORT', '5672')
if rabbitmq_port_env.startswith('tcp://'):
    RABBITMQ_PORT = int(rabbitmq_port_env.split(":")[-1])
else:
    RABBITMQ_PORT = int(rabbitmq_port_env)
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'deploy')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'VMware123!')
CARD_QUEUE_NAME = os.getenv('RABBITMQ_CARD_QUEUE', 'mtgcards') 
SET_QUEUE_NAME = os.getenv('RABBITMQ_SET_QUEUE', 'mtgsets')
MESSAGE_RATE = float(os.getenv('MESSAGE_RATE', 10))

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

LAND_CARD_NAMES = {"Plains", "Island", "Swamp", "Mountain", "Forest"}

def create_connection():
    retry_delay = 5
    max_delay  = 60  # Cap the delay
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials))
            logger.info("Successfully connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.error({"error": str(e), "message": f"Retrying connection in {retry_delay} seconds..."})
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, max_delay)

# Establish connection to RabbitMQ
connection = create_connection()
channel = connection.channel()
channel.queue_declare(queue=CARD_QUEUE_NAME, durable=True, arguments={"x-queue-type": "quorum"})
channel.queue_declare(queue=SET_QUEUE_NAME, durable=True, arguments={"x-queue-type": "quorum"})
logger.info("Successfully declared queues")

def publish_card(card):
    """Publish a card's data to the RabbitMQ queue."""
    try:
        card_message = {
            "name": card.name,
            "mana_cost": card.mana_cost,
            "type": card.type,
            "rarity": card.rarity,
            "set": card.set,
            "text": card.text,
            "power": card.power,
            "toughness": card.toughness,
            "legalities": card.legalities,
            "image_url": card.image_url
        }
        channel.basic_publish(
            exchange='',
            routing_key=CARD_QUEUE_NAME,
            body=str(card_message),
            properties=pika.BasicProperties(
                delivery_mode=2  # Make message persistent
            )
        )
        logger.info(f"Published card: {card.name}")
    except Exception as e:
        logger.error(f"Failed to publish card {card.name}: {e}")

def publish_set(mtg_set, total_cards):
    """Publish a set's data to the RabbitMQ set queue."""
    try:
        set_message = {
            "name": mtg_set.name,
            "code": mtg_set.code,
            "release_date": mtg_set.release_date,
            "total_cards": total_cards
        }
        channel.basic_publish(
            exchange='',
            routing_key=SET_QUEUE_NAME,
            body=str(set_message),
            properties=pika.BasicProperties(
                delivery_mode=2  # Make message persistent
            )
        )
        logger.info(f"Published set: {mtg_set.name}")
    except Exception as e:
        logger.error(f"Failed to publish set {mtg_set.name}: {e}")

def fetch_cards_by_set(mtg_set):
    """Fetch cards and handle HTTP errors with retries."""
    set_code = mtg_set.code
    total_cards = 0
    while True:
        try:
            start_time = datetime.now()
            logger.info(f"{start_time}: Fetching MTG cards in set {set_code}...")

            cards = Card.where(set=set_code).all()

            end_time = datetime.now()
            logger.info(f"{end_time}: Successfully fetched all cards")
            logger.info(f"Total time to fetch cards: {end_time - start_time}")

            for card in cards:
                if card.name in LAND_CARD_NAMES:
                    logger.debug(f"Skipping land card: {card.name}")
                    continue # skipping land cards
                publish_card(card)
                total_cards += 1
                time.sleep(1.0 / MESSAGE_RATE)  # Rate-limiting publishing if specified
            break  # Exit loop if successful

        except HTTPError as e:
            if e.code == 500:
                logger.error("HTTP 500 error encountered. Retrying in 60 seconds...")
                time.sleep(60)
            else:
                logger.error(f"HTTP error encountered: {e}")
                break  # Exit on non-recoverable errors
        except Exception as e:
            logger.error(f"Error fetching cards: {e}")
            break  # Exit loop for unexpected errors
    publish_set(mtg_set, total_cards)

def fetch_and_process_sets():
    """Fetch all card sets and process them one by one"""
    try:
        start_time = datetime.now()
        logger.info(f"{start_time}: Fetch all card sets...")

        sets = Set.all()
        
        end_time = datetime.now()
        logger.info(f"{end_time} Successfully fetched {len(sets)} sets")
        logger.info(f"Total time to fetch sets: {end_time - start_time}")

        for mtg_set in sets:
            logger.info(f"Processing set: {mtg_set.name} (code: {mtg_set.code})")
            fetch_cards_by_set(mtg_set)
    except Exception as e:
        logger.error(f"Error fetching sets: {e}")

# Run the script
if __name__ == "__main__":
    script_start_time = datetime.now()
    logger.info(f"{script_start_time}: Script execution begin")
    
    fetch_and_process_sets()

    script_end_time = datetime.now()
    logger.info(f"{script_end_time}: Script execution complete")
    logger.info(f"Total time to execute script: {script_end_time - script_start_time}")

    # Close connection
    connection.close()
    logger.info("RabbitMQ connection closed.")
