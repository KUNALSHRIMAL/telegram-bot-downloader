# Use official Python 3.11 base image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy code into container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make the start script executable
RUN chmod +x start.sh

# Run the bot
CMD ["bash", "start.sh"]