# Multi-stage Dockerfile for React Frontend
# Optimized for AWS ECS production deployment with security and performance focus

# ============================================================================
# Stage 1: Base Node.js image with optimizations
# ============================================================================
FROM node:18-alpine as base

# Install security updates and essential packages
RUN apk update && apk upgrade && apk add --no-cache \
    dumb-init \
    curl \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# Create non-root user for security
RUN addgroup -g 1001 -S appuser && \
    adduser -u 1001 -S appuser -G appuser

# Set working directory
WORKDIR /app

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# ============================================================================
# Stage 2: Dependencies installation stage
# ============================================================================
FROM base as dependencies

# Switch to non-root user
USER appuser

# Copy package files and install dependencies
COPY --chown=appuser:appuser package*.json ./

# Install production dependencies with npm ci for faster, reliable builds
RUN npm ci --only=production --silent && \
    npm cache clean --force

# ============================================================================
# Stage 3: Development image with hot reload
# ============================================================================
FROM base as development

# Switch to non-root user
USER appuser

# Copy package files
COPY --chown=appuser:appuser package*.json ./

# Install all dependencies (including dev dependencies)
RUN npm install --silent && \
    npm cache clean --force

# Copy source code with proper ownership
COPY --chown=appuser:appuser . .

# Create .env file if it doesn't exist
RUN touch .env

# Development environment variables
ENV NODE_ENV=development \
    REACT_APP_ENV=development \
    GENERATE_SOURCEMAP=true \
    BROWSER=none \
    CHOKIDAR_USEPOLLING=true

# Expose port
EXPOSE 3000

# Health check for development
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start development server with hot reload
ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "start"]

# ============================================================================
# Stage 4: Build stage for production
# ============================================================================
FROM base as build

# Switch to non-root user
USER appuser

# Copy package files
COPY --chown=appuser:appuser package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm ci --silent && \
    npm cache clean --force

# Copy source code
COPY --chown=appuser:appuser . .

# Production build environment variables
ENV NODE_ENV=production \
    REACT_APP_ENV=production \
    GENERATE_SOURCEMAP=false \
    INLINE_RUNTIME_CHUNK=false \
    IMAGE_INLINE_SIZE_LIMIT=0

# Build the application with optimizations
RUN npm run build && \
    # Verify build was successful
    ls -la build/ && \
    # Remove source maps if they exist (extra security)
    find build -name "*.map" -delete

# ============================================================================
# Stage 5: Production image with optimized Nginx
# ============================================================================
FROM nginx:alpine as production

# Install security updates and essential packages
RUN apk update && apk upgrade && apk add --no-cache \
    curl \
    ca-certificates \
    && rm -rf /var/cache/apk/*

# Create non-root user for nginx worker processes
RUN addgroup -g 1001 -S nginx-worker && \
    adduser -u 1001 -S nginx-worker -G nginx-worker

# Copy built application from build stage
COPY --from=build --chown=nginx:nginx /app/build /usr/share/nginx/html

# Copy optimized nginx configuration
COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf

# Create nginx configuration for production
RUN echo 'user nginx-worker;' > /etc/nginx/nginx.conf && \
    echo 'worker_processes auto;' >> /etc/nginx/nginx.conf && \
    echo 'error_log /var/log/nginx/error.log warn;' >> /etc/nginx/nginx.conf && \
    echo 'pid /var/run/nginx.pid;' >> /etc/nginx/nginx.conf && \
    echo 'events {' >> /etc/nginx/nginx.conf && \
    echo '    worker_connections 1024;' >> /etc/nginx/nginx.conf && \
    echo '    use epoll;' >> /etc/nginx/nginx.conf && \
    echo '    multi_accept on;' >> /etc/nginx/nginx.conf && \
    echo '}' >> /etc/nginx/nginx.conf && \
    echo 'http {' >> /etc/nginx/nginx.conf && \
    echo '    include /etc/nginx/mime.types;' >> /etc/nginx/nginx.conf && \
    echo '    default_type application/octet-stream;' >> /etc/nginx/nginx.conf && \
    echo '    sendfile on;' >> /etc/nginx/nginx.conf && \
    echo '    tcp_nopush on;' >> /etc/nginx/nginx.conf && \
    echo '    tcp_nodelay on;' >> /etc/nginx/nginx.conf && \
    echo '    keepalive_timeout 65;' >> /etc/nginx/nginx.conf && \
    echo '    gzip on;' >> /etc/nginx/nginx.conf && \
    echo '    gzip_vary on;' >> /etc/nginx/nginx.conf && \
    echo '    gzip_min_length 1024;' >> /etc/nginx/nginx.conf && \
    echo '    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;' >> /etc/nginx/nginx.conf && \
    echo '    include /etc/nginx/conf.d/*.conf;' >> /etc/nginx/nginx.conf && \
    echo '}' >> /etc/nginx/nginx.conf

# Set proper permissions
RUN chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    chmod -R 755 /usr/share/nginx/html && \
    # Create nginx directories with proper permissions
    mkdir -p /var/cache/nginx/client_temp && \
    chown -R nginx:nginx /var/cache/nginx

# Expose port
EXPOSE 80

# Production health check with better timing
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=5 \
    CMD curl -f http://localhost/health || curl -f http://localhost || exit 1

# Start nginx with proper signal handling
STOPSIGNAL SIGQUIT
CMD ["nginx", "-g", "daemon off;"]

# ============================================================================
# Stage 6: AWS ECS optimized production image
# ============================================================================
FROM production as ecs-production

# ECS-specific optimizations
RUN apk add --no-cache \
    aws-cli \
    jq \
    && rm -rf /var/cache/apk/*

# ECS-optimized nginx configuration with proper logging
RUN echo 'log_format main '"'"'$remote_addr - $remote_user [$time_local] "$request" '"'"' >> /etc/nginx/nginx.conf.d/ecs.conf && \
    echo '                  $status $body_bytes_sent "$http_referer" '"'"' >> /etc/nginx/nginx.conf.d/ecs.conf && \
    echo '                  "$http_user_agent" "$http_x_forwarded_for"'"'"';' >> /etc/nginx/nginx.conf.d/ecs.conf && \
    echo 'access_log /var/log/nginx/access.log main;' >> /etc/nginx/nginx.conf.d/ecs.conf

# ECS health check endpoint
RUN echo 'server {' > /etc/nginx/conf.d/health.conf && \
    echo '    listen 80;' >> /etc/nginx/conf.d/health.conf && \
    echo '    location /health {' >> /etc/nginx/conf.d/health.conf && \
    echo '        access_log off;' >> /etc/nginx/conf.d/health.conf && \
    echo '        return 200 "healthy\n";' >> /etc/nginx/conf.d/health.conf && \
    echo '        add_header Content-Type text/plain;' >> /etc/nginx/conf.d/health.conf && \
    echo '    }' >> /etc/nginx/conf.d/health.conf && \
    echo '}' >> /etc/nginx/conf.d/health.conf

# ECS-optimized health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Signal handling for graceful shutdown in ECS
STOPSIGNAL SIGTERM

# ECS production command with proper signal handling
CMD ["sh", "-c", "exec nginx -g 'daemon off;'"]

# Default target is development
FROM development