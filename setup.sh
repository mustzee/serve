#!/bin/bash
# Setup script for Local LLM Serve

set -e

echo "=== Local LLM Serve Setup ==="
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✓ Docker found"

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker Compose found"

# Create necessary directories
mkdir -p model_cache
echo "✓ Created model_cache directory"

# Start services
echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 5

# Check health
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Server is ready!"
        break
    fi
    echo -n "."
    sleep 1
done

echo ""
echo ""
echo "=== Setup Complete ==="
echo ""
echo "Server is running at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Next steps:"
echo "1. Download a model:"
echo "   docker exec -it llm-ollama ollama pull llama2"
echo "   docker exec -it llm-ollama ollama pull codellama"
echo ""
echo "2. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "3. Run examples:"
echo "   python examples/coding_assistant.py"
echo "   python examples/daily_agent.py"
echo ""
echo "To stop services: docker-compose down"
echo "To view logs: docker-compose logs -f"
