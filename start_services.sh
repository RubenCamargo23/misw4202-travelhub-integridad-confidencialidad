#!/bin/bash
# Startup script for TravelHub microservices
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON=/usr/bin/python3

echo "=== TravelHub Security Services Startup ==="
echo "Project: $PROJECT_DIR"

# Kill any existing services on ports 8000-8002
for PORT in 8000 8001 8002; do
    PID=$(lsof -ti tcp:$PORT 2>/dev/null) && kill -9 $PID 2>/dev/null && echo "Killed process on port $PORT" || true
done
sleep 1

# Start Auth Service (port 8000)
echo "Starting Auth Service on port 8000..."
cd "$PROJECT_DIR/microservicio-auth"
$PYTHON app.py > "$PROJECT_DIR/auth.log" 2>&1 &
AUTH_PID=$!

# Start Audit Service (port 8001)
echo "Starting Audit Service on port 8001..."
cd "$PROJECT_DIR/microservicio-audit"
$PYTHON app.py > "$PROJECT_DIR/audit.log" 2>&1 &
AUDIT_PID=$!

# Start Reservas Service (port 8002)
echo "Starting Reservas Service on port 8002..."
cd "$PROJECT_DIR/microservicio-reservas"
$PYTHON app.py > "$PROJECT_DIR/reservation.log" 2>&1 &
RES_PID=$!

echo "Auth PID: $AUTH_PID | Audit PID: $AUDIT_PID | Reservas PID: $RES_PID"
echo "Waiting for services to initialize..."
sleep 3

# Quick health check
for PORT in 8000 8001 8002; do
    if lsof -ti tcp:$PORT > /dev/null 2>&1; then
        echo "  ✓ Port $PORT is listening"
    else
        echo "  ✗ Port $PORT is NOT listening — check logs"
    fi
done

echo ""
echo "=== Running Validation ==="
cd "$PROJECT_DIR"
$PYTHON validate_plan.py

echo ""
echo "=== Done ==="
echo "Backend services: kill $AUTH_PID $AUDIT_PID $RES_PID"
echo ""
echo "To start the Angular frontend:"
echo "  cd $PROJECT_DIR/frontend-angular"
echo "  npm start    (runs on http://localhost:4200)"
