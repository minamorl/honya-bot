# Use the official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and app files
COPY requirements.txt .
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for Discord bot communication (optional, not required by Discord)
EXPOSE 8000

# Command to run the app
CMD ["python", "bot.py"]
