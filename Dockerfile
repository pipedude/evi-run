FROM python:3.11-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential gcc \
 && rm -rf /var/lib/apt/lists/*

# --- system deps ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl gnupg git && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# --- Jupiter-MCP ---
RUN npm install -g github:pipedude/jupiter-mcp

RUN npm install -g dexpaprika-mcp

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#COPY ./index.js /usr/lib/node_modules/jupiter-mcp/index.js

# Specify the command that will be executed when the container is started
CMD ["python", "-u", "-m", "bot.main"]