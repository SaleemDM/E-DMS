import requests

BASE_URL = "http://localhost:5000"

def test_registration():
    print("Running User Registration Test...")

    # Test 1: Successful Registration
    payload = {
        'username': 'testuser',
        'password': 'password123'
    }
    response = requests.post(f"{BASE_URL}/register", data=payload)
    print("Test 1 - Register New User:", response.text)

    # Test 2: Duplicate Username
    duplicate_response = requests.post(f"{BASE_URL}/register", data=payload)
    print("Test 2 - Duplicate User Check:", duplicate_response.text)

if __name__ == '__main__':
    test_registration()

