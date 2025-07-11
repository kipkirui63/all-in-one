
#!/bin/bash

BASE_URL="http://0.0.0.0:5000"

echo "=========================================="
echo "TESTING API ROUTES WITH CURL"
echo "=========================================="

# Test API status
echo -e "\n1. Testing API Status..."
curl -s -w "Status: %{http_code}\n" "$BASE_URL/api/status/" | head -20

# Test user registration
echo -e "\n2. Testing User Registration..."
curl -s -w "Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User", 
    "email": "test@example.com",
    "phone": "1234567890",
    "password": "testpassword123",
    "repeat_password": "testpassword123"
  }' \
  "$BASE_URL/api/register/" | head -20

# Test user login
echo -e "\n3. Testing User Login..."
curl -s -w "Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }' \
  "$BASE_URL/api/login/" | head -20

# Test tools list
echo -e "\n4. Testing Tools List..."
curl -s -w "Status: %{http_code}\n" "$BASE_URL/api/tools/" | head -20

# Test subscription check
echo -e "\n5. Testing Subscription Check..."
curl -s -w "Status: %{http_code}\n" "$BASE_URL/api/auth/check-subscription/" | head -20

# Test stripe checkout
echo -e "\n6. Testing Stripe Checkout..."
curl -s -w "Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{
    "price_id": "price_test123",
    "success_url": "http://example.com/success",
    "cancel_url": "http://example.com/cancel"
  }' \
  "$BASE_URL/api/stripe/create-checkout/" | head -20

# Test my subscriptions
echo -e "\n7. Testing My Subscriptions..."
curl -s -w "Status: %{http_code}\n" "$BASE_URL/api/my-subscriptions/" | head -20

# Test newsletter subscribe
echo -e "\n8. Testing Newsletter Subscribe..."
curl -s -w "Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newsletter@example.com"
  }' \
  "$BASE_URL/api/newsletter/subscribe" | head -20

# Test contact submit
echo -e "\n9. Testing Contact Submit..."
curl -s -w "Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "contact@example.com", 
    "phone": "1234567890",
    "message": "This is a test message"
  }' \
  "$BASE_URL/api/contact/submit" | head -20

# Test book meeting
echo -e "\n10. Testing Book Meeting..."
curl -s -w "Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "meeting_type": "AI Consultation",
    "preferred_date": "2024-12-31T10:00:00Z",
    "description": "This is a test meeting",
    "timezone": "UTC"
  }' \
  "$BASE_URL/api/meetings/book" | head -20

# Test get meetings
echo -e "\n11. Testing Get Meetings..."
curl -s -w "Status: %{http_code}\n" "$BASE_URL/api/meetings" | head -20

# Test get specific meeting (ID 1)
echo -e "\n12. Testing Get Specific Meeting..."
curl -s -w "Status: %{http_code}\n" "$BASE_URL/api/meetings/1" | head -20

# Test chat
echo -e "\n13. Testing Chat..."
curl -s -w "Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, this is a test message"
  }' \
  "$BASE_URL/api/chat" | head -20

# Test chat session
echo -e "\n14. Testing Chat Session..."
curl -s -w "Status: %{http_code}\n" "$BASE_URL/api/chat/session" | head -20

# Test health check
echo -e "\n15. Testing Health Check..."
curl -s -w "Status: %{http_code}\n" "$BASE_URL/api/health" | head -20

echo -e "\n=========================================="
echo "CURL ROUTE TESTING COMPLETED"
echo "=========================================="
