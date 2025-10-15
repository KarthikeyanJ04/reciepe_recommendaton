#!/bin/bash


echo "=================================="
echo "What Can I Cook? - Docker Setup"
echo "=================================="

# Check if models exist
if [ ! -d "models" ] || [ ! -f "models/recipes.db" ]; then
    echo "❌ ERROR: Models not found!"
    exit 1
fi

echo "✓ Models found"
echo ""

# Build Docker image
echo "Building Docker image..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✓ Build successful"
echo ""

# Start container
echo "Starting container..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start container!"
    exit 1
fi

echo ""
echo "=================================="
echo "✓ Container started successfully!"
echo "=================================="
echo ""
echo "Access the app at: http://localhost:5000"
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose down"
echo "  Restart:      docker-compose restart"
echo "  Status:       docker-compose ps"
echo ""
