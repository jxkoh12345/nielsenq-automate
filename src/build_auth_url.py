import hashlib
import base64
import secrets
import string
import urllib.parse

class AuthUrlGenerator:

    def __init__(self):
       
        # 1. Generate and save the Dynamic Values
        self.state = secrets.token_urlsafe(48)  # ~64 chars
        self.nonce = secrets.token_urlsafe(48)  # ~64 chars
        self.code_verifier = secrets.token_urlsafe(48)  # ~64 chars
        self.redirect_uri = "https://gateway.nielseniq.com/home/login/callback"

        # 2. Generate challenge
        self.code_challenge = self._generate_pkce_challenge(self.code_verifier)
        
        #3. Build url
        self.url = self._build_url()
    

    # def generate_random_string(self, length=64):
    #     """Generates a cryptographically secure random string."""
    #     chars = string.ascii_letters + string.digits
    #     return ''.join(secrets.choice(chars) for _ in range(length))

    def _generate_pkce_challenge(self, verifier):
        """Creates a SHA256 code_challenge from the code_verifier."""
        sha256_hash = hashlib.sha256(verifier.encode('utf-8')).digest()
        # Base64URL encode and remove padding '='
        return base64.urlsafe_b64encode(sha256_hash).decode('utf-8').replace('=', '')
    

    def _build_url(self):
        """Constructs the final authorization URL."""
        
        params = {
            "client_id": "0oa44adypuQ9Zv7Zf4x7",
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
            "nonce": self.nonce,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": self.state,
            "scope": "openid email profile"
        }

        base_url = "https://login.identity.nielseniq.com/oauth2/default/v1/authorize"
        auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
        # print(f"Generated URL:\n{auth_url}")
        return auth_url

    # print(f"RANDOM STRING (state) {state}")
    # print(f"RANDOM STRING (nonce) {nonce}")
    # print(f"CHALLENGE GENERATED FROM VERIFIER: {code_challenge}")
    # print("\n\n")
    # print("--- NEW AUTHENTICATION SESSION ---")
    # print(f"Code Verifier (Save this): {code_verifier}")
    