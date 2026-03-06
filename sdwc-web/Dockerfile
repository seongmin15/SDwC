# Build stage — install dependencies and build static assets
FROM node:20-slim AS builder

WORKDIR /app

COPY sdwc-web/package.json sdwc-web/package-lock.json ./
RUN npm ci

COPY sdwc-web/ ./
RUN npm run build

# Runtime stage — serve static files with nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY sdwc-web/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO /dev/null http://localhost:80/ || exit 1
