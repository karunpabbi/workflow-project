FROM python:3.13-slim-trixie

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

WORKDIR /usr/src/app
COPY src/ src/
COPY pyproject.toml .
COPY README.md .

EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV PYTHONUNBUFFERED=1

CMD ["uv","run" ,"python", "src/workflow_project/app.py"]