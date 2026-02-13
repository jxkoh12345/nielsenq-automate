import requests
import time
import uuid


from oie_login import ObtainAccessToken

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
SEC_HEADERS = {
    "Sec-Ch-Ua": '""Not(A:Brand";v="8", "Chromium";v="144", "Microsoft Edge";v="144"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Ch-Ua-Platform-Version": '"19.0.0"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Okta-User-Agent-Extended": "okta-auth-js/7.14.0 okta-signin-widget-7.39.3",
    "Accept": "application/ion+json; okta-version=1.0.0",
    "Content-Type": "application/ion+json; okta-version=1.0.0",
    "Origin": "https://login.identity.nielseniq.com",
    "Accept-Language": "en-US,en;q=0.9",
}

EMAIL = "ocboon@bigcaring.com.my"
PASSWORD = "2*BR?UC4ihKjcej"
DIR = "export"

session = requests.Session()


handshake = ObtainAccessToken(session=session, userAgent=USER_AGENT, secHeaders=SEC_HEADERS, email=EMAIL, password=PASSWORD)


def run_nielsen_export(session, user_id, output_filename="nielsen_report.xlsx",):

    """
    Complete export workflow: initiate → poll → download
    """

    base_url = "https://apac.connect.nielseniq.com"
    
    # 1. Prepare the standard headers found in your logs
    # We generate a fresh Transaction ID for the initiation
    txn_id = uuid.uuid4().hex.upper()
    
    headers = {
        'origin': base_url,
        'referer': f'{base_url}/discover/my-assets/report/shared-with-me/folder/APAC-91400',
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'source': 'WEB',
        'x-niq-discover-client-home-stack-id': 'APAC',
        'x-niq-discover-txn-origin-stack-id': 'APAC',
        'x-niq-discover-user-home-stack-id': 'APAC',
        'x-nlsn-clnt-app-cd': 'RBOC',
        'x-nlsn-clnt-app-dsply-nm': 'Report Builder On Connect',
        'x-nlsn-clnt-cmpnt-cd': 'RBOC_UI',
        'x-nlsn-clnt-cmpnt-dsply-nm': 'RBOC UI',
        'x-nlsn-orgn-app-cd': 'NDSC',
        'x-nlsn-sub-cmpnt-cd': 'Find My Stuff',
        'x-nlsn-tnxn-id': txn_id,
        'x-nlsn-usr-locale': 'en-GB',
        'x-requested-with': 'XMLHttpRequest',
    }

    # The payload from your Request 1
    # Note: Using the appId from your log: 9916ABBD14EC45B2A7A2B193988C526C
    app_id = "9916ABBD14EC45B2A7A2B193988C526C"
    export_payload = {
        "modified": [],
        "unModified": [
            {"assetId": "APAC-91406", "sourceId": "30dfa2a8-33e8-4091-af68-67c2976b7b84", "reportName": "Brand Ranking Report", "reportType": "layoutEditor", "flowAssetId": "APAC-91402", "reportOrder": 6},
            {"assetId": "APAC-91410", "sourceId": "dbbc54a1-927b-442e-9aad-9b864d41e23b", "reportName": "Category Scorecard - By Segments", "reportType": "layoutEditor", "flowAssetId": "APAC-91402", "reportOrder": 4},
            {"assetId": "APAC-91403", "sourceId": "2e9197d9-0d96-405a-8283-3cb4b97bea10", "reportName": "Executive Summary - Value Analysis", "reportType": "layoutEditor", "flowAssetId": "APAC-91402", "reportOrder": 0},
            {"assetId": "APAC-148919", "sourceId": "6b905c98-db73-4f6c-9bd8-83c6e792688f", "reportName": "Executive Summary - Volume Analysis", "reportType": "layoutEditor", "flowAssetId": "APAC-91402", "reportOrder": 1},
            {"assetId": "APAC-91404", "sourceId": "063c1da6-49b1-4652-babb-b3816699262a", "reportName": "Full SKU Ranking Report", "reportType": "layoutEditor", "flowAssetId": "APAC-91402", "reportOrder": 7},
            {"assetId": "APAC-91409", "sourceId": "159de8ce-8bb1-4cfa-b28f-56db92e0bfd4", "reportName": "Market Share Report (Value)", "reportType": "layoutEditor", "flowAssetId": "APAC-91402", "reportOrder": 2},
            {"assetId": "APAC-97702", "sourceId": "12c6b428-7045-4b7d-8727-a060e19b9711", "reportName": "Market Share Report (Volume)", "reportType": "layoutEditor", "flowAssetId": "APAC-91402", "reportOrder": 3},
            # {"assetId": "APAC-91407", "sourceId": "12c6b428-7045-4b7d-8727-a060e19b9711", "reportName": "Market Share Report (Volume)", "reportType": "layoutEditor", "flowAssetId": "APAC-91402", "reportOrder": 8},
            {"assetId": "APAC-91408", "sourceId": "3c566460-a1fc-4624-9741-a97bd219a34a", "reportName": "Supplier Ranking Report", "reportType": "layoutEditor", "flowAssetId": "APAC-91402", "reportOrder": 5}
        ],
        "userId": f"{user_id}",
        "runAll": True,
        "exportOptions": {
            "exportTitle": "MY - Georgetown Buyer View - Acne",
            "extension": "xlsx",
            "arranged": False,
            "appId": app_id,
            "fmsExport": False,
            "isStatic": False,
            "savedRegion": "APAC",
            "multiply": False,
            "slicebyMultiply": False,
            "assetType": "REPORT",
            "workFlow": "Report",
            "cardSource": "DISCOVERGUIDEDFLOW",
            "smbOrgFlag": False,
            "enableCardsLayout": True,
            "advancedExportOptions": {"persistMasking": False, "hideDatasheets": False}
        }
    }

    # STEP 1: Initiate Export
    print(f"[*] Initiating export job (Txn: {txn_id})...")
    print(f"[*] Identity Cookie Check: {'X-NIQ-USER-INFO' in session.cookies.get_dict()}")
    
    init_url = f"{base_url}/discover-ui-gateway/svc/discover/fe-services/export"
    resp = session.post(init_url, headers=headers, json=export_payload)
    
    if resp.status_code == 200:
        print(resp.json())
        print(f"[+] SUCCESS! Job ID: {resp.json().get('exportId')}")
        export_id = resp.json().get('exportId')
    else:
        print(f"[!] Failed: {resp.status_code}")
        print(resp.text)


    # # STEP 2 & 3: Polling for Status
    status_url = f"{base_url}/discover-ui-gateway/svc/discover/export-services/api/export/status/{export_id}"
    
    max_retries = 30
    print("[*] Waiting for report to generate...")
    
    for i in range(max_retries):
        # Update Txn ID for each poll to look natural
        headers['x-nlsn-tnxn-id'] = uuid.uuid4().hex.upper()
        
        status_resp = session.get(status_url, headers=headers)
        status_data = status_resp.json()
        
        # Adjust 'status' key based on the actual API response structure
        current_status = status_data.get('status', 'UNKNOWN')
        print(f"    > Attempt {i+1}: Status is {current_status}")

        if current_status == "COMPLETED" in str(status_data):
            print("[+] Export ready for download!")
            break
        elif current_status == "FAILED":
            print("[!] Server reported export failure.")
            return
        
        time.sleep(5) # Wait 5 seconds between checks
    else:
        print("[!] Polling timed out.")
        return

    # STEP 4: Download the file
    print(f"[*] Downloading file: {output_filename}")
    download_url = f"{base_url}/discover-ui-gateway/svc/discover/export-services/api/export/{app_id}/download/{export_id}"
    
    headers['x-nlsn-tnxn-id'] = uuid.uuid4().hex.upper()
    final_resp = session.get(download_url, headers=headers, stream=True)

    export_path = f"{DIR}/{output_filename}"

    if final_resp.status_code == 200:
        with open(export_path, 'wb') as f:
            for chunk in final_resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[SUCCESS] File saved as {output_filename}")
    else:
        print(f"[!] Download failed with status {final_resp.status_code}")

# Execution
run_nielsen_export(session, user_id=handshake.user_id)