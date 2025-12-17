FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir requests numpy

# Copy simulator files
COPY simulator.py ml_model.py ./

# Default command (can be overridden in docker-compose)
CMD ["python", "simulator.py", "--plots", "1", "--inject_anomaly", "--anomaly_every", "5", "--username", "farmer1", "--password", "testpw123"]
