import argparse
import json
import os
import random
import time

from kafka import KafkaProducer


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Kafka producer for network traffic data"
    )
    parser.add_argument(
        "--message-limit",
        type=int,
        default=0,
        help="Maximum number of messages to send (default: 0, run indefinitely)",
    )
    args = parser.parse_args()

    # Get Kafka bootstrap server from environment variable
    bootstrap_servers = os.getenv("KAFKA_CLUSTER_BOOTSTRAP_SERVER")
    if not bootstrap_servers:
        raise RuntimeError(
            """KAFKA_CLUSTER_BOOTSTRAP_SERVER environment variable 
        is not set. Please set it to your Kafka bootstrap service address."""
        )

    # Initialize Kafka producer with optimized settings
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        # Performance optimizations
        batch_size=16384,  # batch size 16 KB
        linger_ms=5,  # Wait up to 5ms for more messages to batch
        compression_type="gzip",  # Enable compression
        buffer_memory=33554432,  # 32MB buffer
        max_request_size=1048576,  # 1MB max request size
        retries=3,
        acks=1,  # Leader acknowledgment only for better throughput
    )

    print("Starting to send messages...")
    start_time = time.time()
    message_count = 0

    # First, read all lines into memory for random sampling
    with open("pcap_dump.jsonlines") as file:
        all_lines = file.readlines()

    print(f"Loaded {len(all_lines)} lines into memory for sampling")

    try:
        while True:
            # Check if we've reached the message limit
            if args.message_limit > 0 and message_count >= args.message_limit:
                print(f"\nReached message limit of {args.message_limit}")
                break

            # Randomly sample a line
            random_line = random.choice(all_lines)

            try:
                # Parse the line as JSON
                data = json.loads(random_line.strip())
                # Send to Kafka asynchronously
                producer.send("network-traffic-input", data)
                message_count += 1

                # Print progress every 10000 messages
                if message_count % 10000 == 0:
                    print(f"Sent {message_count} messages...")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                continue

    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, stopping...")

    finally:
        # Flush and close the producer
        producer.flush()
        producer.close()

        end_time = time.time()
        duration = end_time - start_time
        messages_per_second = message_count / duration

        print("\nData publishing complete!")
        print(f"Total messages sent: {message_count}")
        print(f"Total time: {duration:.2f} seconds")
        print(f"Messages per second: {messages_per_second:.2f}")


if __name__ == "__main__":
    main()
