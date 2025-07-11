
#!/bin/bash

echo "Starting Django server in background..."
python manage.py runserver 0.0.0.0:3000 &
SERVER_PID=$!

echo "Waiting for server to start..."
sleep 5

echo "Running route tests..."
python test_routes.py

echo "Stopping server..."
kill $SERVER_PID

echo "Tests completed!"
