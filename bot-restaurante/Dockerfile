# Bot de restaurante · docker build -t restaurante-bot . && docker run -p 3000:3000 --env-file .env -v $PWD/data:/data restaurante-bot
FROM node:22-alpine
RUN apk add --no-cache tzdata
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY . .
ENV NODE_ENV=production TZ=America/Tegucigalpa DATA_DIR=/data PORT=3000
RUN mkdir -p /data && chown node:node /data
USER node
VOLUME /data
EXPOSE 3000
CMD ["node", "server.js"]
