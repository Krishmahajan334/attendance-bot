# Use the official Playwright image which includes Python and Browsers
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set up work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromium browser for Playwright
RUN playwright install --with-deps chromium

# Copy app code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Expose the port
EXPOSE 5000

# Run with Gunicorn (increased timeout for long-running checks)
CMD gunicorn --bind 0.0.0.0:$PORT --timeout 600 --workers 1 --threads 4 app:app
