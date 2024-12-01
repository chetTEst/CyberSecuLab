import secrets

def generate_token(length=64):
    return secrets.token_urlsafe(length)

token = generate_token()
print(token)
