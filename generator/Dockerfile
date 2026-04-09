# =============================================================================
# Generator Dockerfile
# Save as: qsim/generator/Dockerfile
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY factory_gen.py .

RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Generator runs as a long-lived process, no port needed
CMD ["python", "factory_gen.py"]
