# Use official Node.js runtime
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY backend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY backend/ .
COPY frontend/ ./frontend/

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", "server.js"]
