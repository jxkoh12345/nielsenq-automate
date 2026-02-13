import requests
import re
import json

from build_auth_url import AuthUrlGenerator



class GenerateStateHandle:

    def __init__(self, session, userAgent, secHeaders):
        
        self.session = session
        self.session.headers.update({
            "User-Agent": userAgent,
        })
        self.secHeaders = secHeaders
        
        self.auth_url_generator = AuthUrlGenerator()
        self.auth_url = self.auth_url_generator.url
        # Determine the Redirect URI (The page we land on) to use as Referer
        self.landing_page_url = None 
        self.state_token = self._generate_state_token()
        self.state_handle = self._obtain_state_handle()


        
      

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
    
    def _obtain_state_handle(self):
        print("[*] Exchanging stateToken for a stateHandle...")
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