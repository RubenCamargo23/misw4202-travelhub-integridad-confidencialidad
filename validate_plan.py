import requests
import time
import sqlite3
import os

BASE_AUTH = "http://localhost:8000"
BASE_AUDIT = "http://localhost:8001"
BASE_RES = "http://localhost:8002"

def test_h1_integrity():
    print("\n--- Testing H1: Integrity & Audit ---")
    
    # 1. Login as Admin (AR)
    resp = requests.post(f"{BASE_AUTH}/login", data={"username": "admin_ar", "password": "admin123"})
    token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Attempt to modify a CONFIRMED reservation (ID 2 is confirmed per init_db)
    print("Attempting to modify CONFIRMED reservation...")
    start = time.time()
    resp = requests.put(f"{BASE_RES}/reservas/2", json={"email": "hacker@test.com"}, headers=headers)
    end = time.time()
    
    print(f"Status: {resp.status_code} (Expected 403)")
    print(f"Response Time: {end - start:.4f}s (Expected < 1s)")
    
    # 4. Verify audit log exists
    print("Checking audit logs...")
    resp = requests.get(f"{BASE_AUDIT}/audit/verify", headers=headers)
    logs = resp.json()
    attempt_logged = any(l["accion"] == "ILLEGAL_MUTATION_ATTEMPT" and l["entidad_id"] == "2" for l in logs)
    print(f"Illegal attempt logged: {attempt_logged}")
    
    # 5. Verify HMAC integrity
    all_verified = all(l["verified"] == True for l in logs)
    print(f"All audit hashes verified: {all_verified}")

def test_h2_confidentiality():
    print("\n--- Testing H2: Confidentiality & ABAC ---")
    
    # 1. Login as User CO
    resp = requests.post(f"{BASE_AUTH}/login", data={"username": "user_co", "password": "user123"})
    token_co = resp.json()["token"]
    headers_co = {"Authorization": f"Bearer {token_co}"}
    
    # 2. Access AR reservation with CO user
    print("Accessing AR reservation with CO user...")
    resp = requests.get(f"{BASE_RES}/reservas/1", headers=headers_co)
    print(f"Status: {resp.status_code} (Expected 403)")
    
    # 3/4. Verify encryption in DB
    print("Verifying encryption in reservas.db...")
    db_path = os.path.join(os.path.dirname(__file__), "instance", "reservations.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT email_cifrado FROM reserva WHERE id=1")
    encrypted_val = cursor.fetchone()[0]
    conn.close()
    
    is_encrypted = not ("test_ar@example.com" in encrypted_val)
    print(f"Data is encrypted in DB: {is_encrypted}")
    print(f"Encrypted value snippet: {encrypted_val[:20]}...")
    
    # 5. Access AR reservation with AR admin
    print("Accessing AR reservation with AR user...")
    resp = requests.post(f"{BASE_AUTH}/login", data={"username": "admin_ar", "password": "admin123"})
    token_ar = resp.json()["token"]
    headers_ar = {"Authorization": f"Bearer {token_ar}"}
    resp = requests.get(f"{BASE_RES}/reservas/1", headers=headers_ar)
    data = resp.json()
    print(f"Decrypted email: {data['email']} (Expected test_ar@example.com)")

if __name__ == "__main__":
    time.sleep(2) # Wait for services to start
    try:
        test_h1_integrity()
        test_h2_confidentiality()
    except Exception as e:
        print(f"Validation failed: {e}")
