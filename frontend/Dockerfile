FROM node:18-alpine

WORKDIR /app

# Copy package.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy app
COPY . .

# Build
RUN npm run build

# Expose port
EXPOSE 3000

# Run
CMD ["npm", "run", "dev"]
