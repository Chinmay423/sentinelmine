#!/bin/bash

# SentinelMine Startup Script
# This script starts all SentinelMine services to provide a fully functional demo

echo "Starting SentinelMine Services..."
echo "=================================="

# Set environment variables
export NODE_ENV=development
export REACT_APP_API_URL=http://localhost:5000
export ML_API_URL=http://localhost:5001
export BLOCKCHAIN_API_URL=http://localhost:5002
export JWT_SECRET=demo-secret-key-for-development-only

# Create a temporary .env file for the services
cat > .env <<EOL
NODE_ENV=development
REACT_APP_API_URL=http://localhost:5000
ML_API_URL=http://localhost:5001
BLOCKCHAIN_API_URL=http://localhost:5002
JWT_SECRET=demo-secret-key-for-development-only
EOL

# Ensure directories exist
mkdir -p logs

# Start API service
echo "Starting API service on port 5000..."
cd src/api
npm start > ../../logs/api.log 2>&1 &
API_PID=$!
cd ../..
echo "API service started with PID: $API_PID"

# Start ML service
echo "Starting ML service on port 5001..."
cd src/ml
python app.py > ../../logs/ml.log 2>&1 &
ML_PID=$!
cd ../..
echo "ML service started with PID: $ML_PID"

# Start Frontend service
echo "Starting Frontend on port 3000..."
cd src/frontend
npm start > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..
echo "Frontend started with PID: $FRONTEND_PID"

# Wait for services to start
echo "Waiting for services to start up..."
sleep 5

# Output information
echo ""
echo "SentinelMine is now running!"
echo "============================"
echo "Frontend: http://localhost:3000"
echo "API: http://localhost:5000"
echo "ML Service: http://localhost:5001"
echo ""
echo "Login Credentials:"
echo "  Username: analyst1"
echo "  Password: password123"
echo ""
echo "To stop all services, run: ./stop-sentinelmine.sh"
echo ""

# Create stop script
cat > stop-sentinelmine.sh <<EOL
#!/bin/bash
echo "Stopping SentinelMine services..."
kill $FRONTEND_PID $API_PID $ML_PID
echo "Services stopped."
EOL

chmod +x stop-sentinelmine.sh

# Open browser (works on most platforms)
if command -v xdg-open > /dev/null; then
  xdg-open http://localhost:3000
elif command -v open > /dev/null; then
  open http://localhost:3000
elif command -v start > /dev/null; then
  start http://localhost:3000
fi 