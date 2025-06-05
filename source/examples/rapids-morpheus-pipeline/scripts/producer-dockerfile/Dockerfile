FROM python:3.12-slim

# Copy application files
COPY producer.py /workspace/producer.py
COPY pcap_dump.jsonlines /workspace/pcap_dump.jsonlines

WORKDIR /workspace

# Install kafka-python 
RUN pip install kafka-python==2.2.3

# Run the script (this uses the --message-limit default to override add in docker run)
ENTRYPOINT ["python", "producer.py"]