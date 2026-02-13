import requests
import re
import json
from urllib.parse import urlparse, parse_qs

from build_auth_url import AuthUrlGenerator



class ObtainAccessToken:

    def __init__(self, session, userAgent, secHeaders, email, password):
        
        self.session = session
        self.session.headers.update({
            "User-Agent": userAgent,
        })
        self.secHeaders = secHeaders
        self.auth_url_generator = AuthUrlGenerator()
        self.auth_url = self.auth_url_generator.url
        self.code_verifier = self.auth_url_generator.code_verifier
        self.redirect_uri = self.auth_url_generator.redirect_uri

        self.user_id = None

        # Determine the Redirect URI (The page we land on) to use as Referer
        self.landing_page_url = None 
        self.state_token = self._generate_state_token()
        self.initial_state_handle = self._obtain_initial_state_handle()
        
        self.challenge_url, self.identify_state_handle = self._identify_user(email)
        self.success_redirect_url = self._submit_password(password)
        self.auth_code, self.state_value = self._redeem_auth_code()
        self.access_token = self._get_access_token()

        # if self.access_token:
        #     self._finalize_application_session()

        if self.access_token:
            # 2. Skip the old finalize. Go straight to the Regional Handshake.
            self._finalize_apac_session()



      

    def _generate_state_token(self):

        # 2. Get the HTML page
        print("[*] Requesting Login Page...")
        response = self.session.get(self.auth_url)


        print(f"Login page: {response}")
        self.landing_page_url = response.url

        
        # 3. Extract the stateToken from the HTML using Regex
        # We are looking for "stateToken":"(the_token)"
        token_match = re.search(r'"stateToken"\s*:\s*"([^"]+)"', response.text)

        if token_match:
            initial_state_token = token_match.group(1)
            # Important: Okta sometimes escapes slashes (e.g. \/) in HTML, let's fix that
            initial_state_token = initial_state_token.replace('\\/', '/')

            # Decode escape sequences
            initial_state_token = bytes(initial_state_token, 'utf-8').decode('unicode_escape')

            print(f"[+] Found Initial State Token: ...{initial_state_token[-20:]}")
            return initial_state_token
        else:
            print("[-] Could not find stateToken in HTML!")
            exit()
    
    def _obtain_initial_state_handle(self):
        print("[*] Exchanging stateToken for a Initial stateHandle...")
        introspect_url = "https://login.identity.nielseniq.com/idp/idx/introspect"
        intro_payload = {"stateToken": self.state_token}

        headers = self.secHeaders.copy()
        headers["Referer"] = self.landing_page_url

        intro_response = self.session.post(introspect_url, json=intro_payload, headers=headers)
        intro_data = intro_response.json()

        # Extract the real stateHandle from the remediation block
        # It's usually found in: remediation -> value[0] -> value[last item]
        try:
            # We look for the 'identify' remediation specifically
            remediations = intro_data['remediation']['value']
            identify_step = next(item for item in remediations if item['name'] == 'identify')
            
            # Within 'identify', find the field named 'stateHandle'
            state_handle = next(f['value'] for f in identify_step['value'] if f['name'] == 'stateHandle')
            print("[+] Successfully obtained stateHandle")
        except (KeyError, StopIteration) as e:
            print("[-] Failed to find stateHandle in Introspect response")
            print(intro_data)
            exit()

        return state_handle





    def _identify_user(self, email):
        identify_url = "https://login.identity.nielseniq.com/idp/idx/identify"
        payload = {
            "identifier": email,
            "stateHandle": self.initial_state_handle,
        }

        headers = self.secHeaders.copy()
        headers["Referer"] = self.landing_page_url

        response = self.session.post(identify_url, json=payload, headers=headers)
        identify_data = response.json()

        try:
            # 1. Find the 'challenge-authenticator' remediation block
            challenge_block = next(
                item for item in identify_data['remediation']['value'] 
                if item.get('name') == 'challenge-authenticator'
            )
            
            # 2. Extract the URL
            challenge_url = challenge_block['href']
            
            # 3. Extract the stateHandle from the 'value' array within the block
            state_handle = next(
                field['value'] for field in challenge_block['value'] 
                if field.get('name') == 'stateHandle'
            )
            
            # print(f"CHALLENGE URL: {challenge_url}")
            # print(f"CHALLENGE STATEHANDLE: {state_handle}")


            return challenge_url, state_handle
        
        except (KeyError, StopIteration) as e:
            print(f"[-] Could not find 'challenge-authenticator' remediation in the response. Error: {e}")
            return None, None

        

    def _submit_password(self, password):

        """
        Submits the user's password to the /challenge/answer endpoint.

        :param password: The user's password.
        :return: The JSON response from the password submission.
        """

        answer_url = self.challenge_url
        payload = {
            "credentials": {
                "passcode": password
            },
            "stateHandle": self.identify_state_handle,
        }

        headers = self.secHeaders.copy()
        headers["Referer"] = self.landing_page_url

        response = self.session.post(answer_url, json=payload, headers=headers)
        answer_data = response.json()

        # print(f"ANSWER RESPONSE {answer_data}")

        try:
            redirect_url = answer_data['success']['href']
            print(f"[+] Found success-redirect URL.")
            # Note: The 'stateToken' in the URL is truncated in your response but will be complete in the real response.
            return redirect_url
        
        except KeyError:
            print("[-] Could not find 'success' block in the response.")
            return None
        

    
    def _redeem_auth_code(self):
        """
        Performs a GET request to the success-redirect URL to obtain the Authorization Code.
        
        :param url: The success redirect url from successful /answer api call

        :return: A tuple of (Authorization Code string, State string) or (None, None) on failure.
        """
        print("[*] Redeeming session for Authorization Code...")

        success_url = self.success_redirect_url

        headers = self.secHeaders.copy()
        headers["Referer"] = self.landing_page_url

        response = self.session.get(success_url, headers=headers, allow_redirects=False)

        final_auth_code_url = response.headers.get('location')

        # Parse the URL into its components
        parsed_url = urlparse(final_auth_code_url)
        
        # Parse the query string into a dictionary
        query_params = parse_qs(parsed_url.query)
        
        # Extract the 'code' and 'state' values
        # parse_qs returns a list for each key, so we take the first element [0]
        auth_code = query_params.get('code', [None])[0]
        state_value = query_params.get('state', [None])[0]

        return auth_code, state_value
    


    def _get_access_token(self):
        """
        Performs the final PKCE Token Exchange POST request.
        """

        if not self.auth_code or not self.code_verifier:
            print("[-] Cannot get tokens: Auth Code or Code Verifier is missing.")
            return None
            
        print("[*] Performing final Token Exchange POST...")
            
        TOKEN_ENDPOINT = 'https://login.identity.nielseniq.com/oauth2/default/v1/token'

        token_payload = {
            'grant_type': 'authorization_code',
            'code': self.auth_code,
            'redirect_uri': self.redirect_uri,
            'client_id': "0oa44adypuQ9Zv7Zf4x7",
            'code_verifier': self.code_verifier
        }

        try:
            token_response = self.session.post(
                TOKEN_ENDPOINT, 
                data=token_payload, 
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )

            token_response.raise_for_status() # Raise an exception for bad status codes

            tokens = token_response.json()
            print("[***] Final Success! Access Tokens Received.")
            return tokens["access_token"]

        except requests.exceptions.HTTPError as e:
            print(f"[---] Token Exchange Failed. HTTP Error: {e}")
            print(f"Response: {token_response.text}")
            return None
        except Exception as e:
            print(f"[---] An unexpected error occurred during token exchange: {e}")
            return None
        
    def _finalize_application_session(self):
        """
        Executes the final GET request to the NielsenIQ application's callback 
        to complete the session hand-off and capture all application cookies 
        (like X-NIQ-USER-INFO). This is essential for subsequent API calls.
        """
        print("[*] Performing final application session hand-off...")

        # 1. The URL where the application receives the code and token 
        #    (The same endpoint used in your final successful IDX redirect)
        FINAL_APP_URL = f"{self.redirect_uri}?code={self.auth_code}&state={self.state_value}"
        
        # 2. Define the headers for the application's domain (not the Okta domain)
        app_headers = {
            "User-Agent": self.session.headers.get("User-Agent"),
            "Referer": "https://login.identity.nielseniq.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Sec-Fetch-Dest": "document", 
            "Sec-Fetch-Mode": "navigate", 
            "Sec-Fetch-Site": "cross-site", # Changed to cross-site as we move from Okta -> NIQ
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }
        
        try:
            response = self.session.get(FINAL_APP_URL, headers=app_headers, allow_redirects=True)
            response.raise_for_status()

            # Check if we got the cookie immediately (Server-Side Flow)
            if self.session.cookies.get('X-NIQ-USER-INFO'):
                print("[***] SUCCESS! Cookie 'X-NIQ-USER-INFO' captured immediately.")
                return

            print("[-] Callback returned SPA/HTML (Status 200). Proceeding to Token Injection...")

            # 2. TOKEN INJECTION (The "Missing Link")
            # We use the access_token to hit the application root. 
            # This mimics the SPA sending the token to the backend, triggering cookie issuance.
            
            injection_url = "https://gateway.nielseniq.com/home/" # Hitting the app root
            
            injection_headers = app_headers.copy()
            # CRITICAL: Authorize with the token we just got
            injection_headers["Authorization"] = f"Bearer {self.access_token}" 
            # Change accept to JSON just in case the backend prefers it for auth checks
            injection_headers["Accept"] = "*/*" 

            print(f"[*] Injecting Access Token to: {injection_url}")
            inj_response = self.session.get(injection_url, headers=injection_headers)
            
            # 3. Final Verification
            niq_cookie = self.session.cookies.get('X-NIQ-USER-INFO')
            if niq_cookie:
                print(f"[***] FINAL SUCCESS! Session Stabilized. Cookie captured: {niq_cookie[:20]}...")
            else:
                print("[!] CRITICAL WARNING: Cookie still missing.")
                print("    However, we have a valid Access Token.")
                print("    The Export API might accept 'Authorization: Bearer <token>' instead of the cookie.")
                print(f"    Token: {self.access_token[:20]}...")

        except Exception as e:
            print(f"[-] Final Hand-off Failed: {e}")
        
    
    def _finalize_apac_session(self):
        """
        Forcefully exchanges the Okta Access Token for NielsenIQ Session Cookies
        on the APAC Regional Server.
        """
        print("\n[*] Initiating Regional Handshake (APAC)...")

        # The endpoint identified in your browser logs
        TARGET_URL = "https://apac.connect.nielseniq.com/portalapi/v5/me"
        
        # Headers mimicking your browser CURL, but adding the Authorization Token
        headers = {
            "User-Agent": self.session.headers.get("User-Agent"),
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Referer": "https://apac.connect.nielseniq.com/discover/",
            "Origin": "https://apac.connect.nielseniq.com",
            
            # --- THE KEY: We swap the Cookies for the Token to start the session ---
            "Authorization": f"Bearer {self.access_token}", 
            
            # --- APP SPECIFIC HEADERS (From your Curl) ---
            "x-nlsn-clnt-app-cd": "RBOC",
            "x-nlsn-clnt-app-dsply-nm": "Report Builder On Connect",
            "x-nlsn-orgn-app-cd": "NDSC",
            "x-nlsn-tnxn-id": "9F8CF07013034507B843DAB1D108B1F6", # Static ID usually fine for handshake
            "Source": "WEB"
        }
        
        try:
            print(f"[*] Sending Access Token to: {TARGET_URL}")
            response = self.session.get(TARGET_URL, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            self.user_id = response.json()["id"]
            # print(response.json()["id"])

            # Debug: Print ALL cookies received
            print("--- Received Cookies ---")
            for cookie in self.session.cookies:
                print(f"  {cookie.name}: {cookie.value[:20]}...")
                
            # Validation
            if response.status_code == 200:
                print("[***] SUCCESS! APAC Session Established.")
                
                # We expect NIQSESSION cookies, but let's check for ANY cookies
                if len(self.session.cookies) > 0:
                    print("[+] Cookies are present. Ready for Export.")
                else:
                    print("[!] Warning: 200 OK received, but no cookies found in jar.")
                    
            else:
                print(f"[-] Handshake Failed. Response: {response.text[:300]}")

        except Exception as e:
            print(f"[-] Error during APAC handshake: {e}")
        

