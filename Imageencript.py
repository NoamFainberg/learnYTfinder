import base64

with open("MyLogo.png", "rb") as f:
    data = f.read()
    encoded = base64.b64encode(data).decode()

with open("encoded_logo.txt", "w") as out:
    out.write(encoded)

print("✅ Base64 string written to 'encoded_logo.txt'")