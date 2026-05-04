#!/bin/bash
# Health check script for Futures Brokiepedia

echo "🏥 Futures Brokiepedia Health Check"
echo "=================================="

# Check QuestDB
echo -n "QuestDB: "
if curl -s http://localhost:9000 > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Down"
fi

# Check ChromaDB
echo -n "ChromaDB: "
if curl -s http://localhost:8000/api/v1/heartbeat > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Down"
fi

# Check Daemon API
echo -n "Daemon API: "
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Down"
fi

# Check Docker containers
echo ""
echo "Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep futures- || echo "No containers running"

echo ""
echo "Disk Usage:"
df -h /opt/futures-brokiepedia 2>/dev/null || df -h /

echo ""
echo "Memory Usage:"
free -h | grep "Mem:" || echo "N/A"
