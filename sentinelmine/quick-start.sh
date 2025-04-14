#!/bin/bash

# Quick Start SentinelMine Frontend
echo "Starting SentinelMine Frontend (Quick Mode)..."

# Create a directory for logs
mkdir -p logs

# Start the frontend service directly
cd src/frontend
echo "Starting Frontend on port 3000..."
npm start > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

echo ""
echo "SentinelMine Frontend is starting!"
echo "=================================="
echo "Access the application at: http://localhost:3000"
echo ""
echo "Login Credentials:"
echo "  Username: analyst1"
echo "  Password: password123"
echo ""
echo "NOTE: Backend services are mocked in this quick-start mode"
echo "To stop the application, press Ctrl+C or run:"
echo "kill $FRONTEND_PID"
echo ""

# Create stop script
cat > quick-stop.sh <<EOL
#!/bin/bash
echo "Stopping SentinelMine frontend..."
kill $FRONTEND_PID
echo "Frontend stopped."
EOL

chmod +x quick-stop.sh

# Open browser
if command -v xdg-open > /dev/null; then
  xdg-open http://localhost:3000
elif command -v open > /dev/null; then
  open http://localhost:3000
elif command -v start > /dev/null; then
  start http://localhost:3000
fi

# Wait for the frontend process
wait $FRONTEND_PID 