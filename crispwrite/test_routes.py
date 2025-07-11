
import requests
import json
from datetime import datetime

BASE_URL = "http://0.0.0.0:3000"

def test_api_routes():
    """Test all API routes"""
    
    print("=" * 50)
    print("TESTING API ROUTES")
    print("=" * 50)
    
    # Test API status
    print("\n1. Testing API Status...")
    try:
        response = requests.get(f"{BASE_URL}/api/status/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test user registration
    print("\n2. Testing User Registration...")
    try:
        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone": "1234567890",
            "password": "testpassword123",
            "repeat_password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/api/register/", json=user_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test user login
    print("\n3. Testing User Login...")
    try:
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/api/login/", json=login_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test tools list
    print("\n4. Testing Tools List...")
    try:
        response = requests.get(f"{BASE_URL}/api/tools/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test subscription check
    print("\n5. Testing Subscription Check...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/check-subscription/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test stripe checkout
    print("\n6. Testing Stripe Checkout...")
    try:
        checkout_data = {
            "price_id": "price_test123",
            "success_url": "http://example.com/success",
            "cancel_url": "http://example.com/cancel"
        }
        response = requests.post(f"{BASE_URL}/api/stripe/create-checkout/", json=checkout_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test my subscriptions
    print("\n7. Testing My Subscriptions...")
    try:
        response = requests.get(f"{BASE_URL}/api/my-subscriptions/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test newsletter subscribe
    print("\n8. Testing Newsletter Subscribe...")
    try:
        newsletter_data = {
            "email": "newsletter@example.com"
        }
        response = requests.post(f"{BASE_URL}/api/newsletter/subscribe", json=newsletter_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test contact submit
    print("\n9. Testing Contact Submit...")
    try:
        contact_data = {
            "name": "Test User",
            "email": "contact@example.com",
            "phone": "1234567890",
            "message": "This is a test message"
        }
        response = requests.post(f"{BASE_URL}/api/contact/submit", json=contact_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test book meeting
    print("\n10. Testing Book Meeting...")
    try:
        meeting_data = {
            "title": "Test Meeting",
            "description": "This is a test meeting",
            "scheduled_time": "2024-12-31T10:00:00Z"
        }
        response = requests.post(f"{BASE_URL}/api/meetings/book", json=meeting_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test get meetings
    print("\n11. Testing Get Meetings...")
    try:
        response = requests.get(f"{BASE_URL}/api/meetings")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test get specific meeting (ID 1)
    print("\n12. Testing Get Specific Meeting...")
    try:
        response = requests.get(f"{BASE_URL}/api/meetings/1")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test chat
    print("\n13. Testing Chat...")
    try:
        chat_data = {
            "message": "Hello, this is a test message"
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test chat session
    print("\n14. Testing Chat Session...")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/session")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test health check
    print("\n15. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("ROUTE TESTING COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    test_api_routes()
