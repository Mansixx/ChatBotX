FROM node:20-alpine AS ui-builder
WORKDIR /ui
COPY ui/package*.json ./
RUN npm install
COPY ui/ ./
RUN npm run build

FROM python:3.10-slim
RUN apt-get update && apt-get install -y gcc g++ make && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY data/ ./data/
COPY domain.yml config.yml endpoints.yml credentials.yml ./
COPY actions/ ./actions/
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt rasa==3.6.20 rasa-sdk==3.6.2
COPY --from=ui-builder /ui/dist ./ui/dist
RUN rasa train --fixed-model-name crisis-bot

EXPOSE 7860

RUN echo '#!/bin/bash\nrasa run actions --port 5055 &\nrasa run --enable-api --cors "*" --port 5005 &\npython -m http.server 7860 --directory ui/dist' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]