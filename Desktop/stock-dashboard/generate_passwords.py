import streamlit_authenticator as stauth

# Create hasher instance (no arguments)
hasher = stauth.Hasher()

# Generate hashed passwords
passwords = ['admin123', 'demo123']
hashed_passwords = []

for password in passwords:
    hashed_password = hasher.hash(password)
    hashed_passwords.append(hashed_password)

print("Hashed passwords:")
for i, hashed in enumerate(hashed_passwords):
    print(f"Password {i+1}: {hashed}")
