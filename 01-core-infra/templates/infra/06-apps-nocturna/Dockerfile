FROM node:20-slim

WORKDIR /app

# Install bun (needed for bun.lock)
RUN npm install -g bun

# Copy package files first for layer caching
COPY package.json bun.lock ./
COPY .env.example .env

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source
COPY . .

# Build frontend
RUN npm run build

# Expose port
EXPOSE 3000

# Run server
CMD ["node", "dist/server.cjs"]