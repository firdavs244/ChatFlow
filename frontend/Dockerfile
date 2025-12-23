# ===========================================
# ChatFlow Frontend - Next.js
# Development Dockerfile
# ===========================================

FROM node:20-alpine

WORKDIR /app

# Install dependencies first
COPY package.json ./
RUN npm install

# Copy source code
COPY . .

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

# Run as root (no user switching for development)
CMD ["npm", "run", "dev"]
