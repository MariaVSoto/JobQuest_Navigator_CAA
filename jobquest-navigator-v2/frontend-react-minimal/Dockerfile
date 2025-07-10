# Multi-stage Dockerfile for React Frontend

# Stage 1: Base Node.js image
FROM node:18-alpine as base

# Set working directory
WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Stage 2: Development image with hot reload
FROM base as development

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies)
RUN npm ci

# Copy source code
COPY . .

# Create .env file if it doesn't exist
RUN touch .env

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start development server with hot reload
ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "start"]

# Stage 3: Build stage for production
FROM base as build

# Copy package files
COPY package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Set production environment variables
ENV REACT_APP_ENV=production
ENV GENERATE_SOURCEMAP=false

# Build the application
RUN npm run build

# Stage 4: Production image with Nginx
FROM nginx:alpine as production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built application from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

# Default target is development
FROM development