# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Set environment variables (you should inject these securely in production)
ENV API_ID=1814711
ENV API_HASH=a14491784f65c3bc76afad00c5f280ba
ENV BOT_TOKEN=7920468776:AAEdU_0VNzCvVVT8U96oC1qoV89IGz2Q6qE

# Run the bot
CMD ["python", "bot.py"]