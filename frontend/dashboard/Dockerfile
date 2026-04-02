# Frontend Dockerfile for Next.js Dashboard
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY frontend/dashboard/package.json frontend/dashboard/package-lock.json ./
RUN npm ci

# Copy Source
COPY frontend/dashboard/ .

# Build
RUN npm run build

# Expose
EXPOSE 3000

CMD ["npm", "start"]
