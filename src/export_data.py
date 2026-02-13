import requests
import uuid
import time

class ExportData:
    def __init__(self, session, data, apiHeaders, fileName, appId, userId, title):
        self.asset_data = self._asset_data_builder(data)
        self.export_payload = self._build_export_payload(self.asset_data, appId, userId, title)

        self.export = self._export_data(session, self.export_payload, apiHeaders, fileName, appId)


    def _asset_data_builder(self, asset_data):
        data = []
        duplicate_checker = set()
        for asset in asset_data:
            #duplicates management
            if(asset["sourceId"] not in duplicate_checker):
                duplicate_checker.add(asset["sourceId"])
                payload_data = {
                    "assetId": asset["assetId"],
                    "sourceId": asset["sourceId"],
                    "reportName": asset["title"],
                    "reportType": "layoutEditor",
                    "flowAssetId" : asset["parentAsset"]["assetId"],
                    "reportOrder" : 0
                }
                data.append(payload_data)
        
        return data

    def _build_export_payload(self, assetData, app_id, user_id, export_title):
        
        export_payload = {
        "modified": [],
        "unModified": assetData,
        "userId": user_id,
        "runAll": True,
        "exportOptions": {
            "exportTitle": export_title,
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

        return export_payload
    
    def _export_data(self, session:requests.Session, payload, headers, output_filename, appId):

        txn_id = uuid.uuid4().hex.upper()
        base_url = "https://apac.connect.nielseniq.com"
        # STEP 1: Initiate Export
        print(f"[*] Initiating export job (Txn: {txn_id})...")
        print(f"[*] Identity Cookie Check: {'X-NIQ-USER-INFO' in session.cookies.get_dict()}")
        
        init_url = f"{base_url}/discover-ui-gateway/svc/discover/fe-services/export"
        resp = session.post(init_url, headers=headers, json=payload)
        
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
        download_url = f"{base_url}/discover-ui-gateway/svc/discover/export-services/api/export/{appId}/download/{export_id}"
        
        headers['x-nlsn-tnxn-id'] = uuid.uuid4().hex.upper()
        final_resp = session.get(download_url, headers=headers, stream=True)

        export_path = output_filename

        if final_resp.status_code == 200:
            with open(export_path, 'wb') as f:
                for chunk in final_resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[SUCCESS] File saved as {output_filename}")
        else:
            print(f"[!] Download failed with status {final_resp.status_code}")
        
    