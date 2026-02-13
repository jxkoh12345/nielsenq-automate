import json
import requests
import subprocess
from export_data import ExportData
import headers_file
from oie_login import ObtainAccessToken
from get_asset_data import GetAssetData
from save_asset_data import AssetDataDB

user_agent = headers_file.USER_AGENT
api_headers = headers_file.API_HEADERS
login_header = headers_file.LOGIN_HEADERS
email = headers_file.EMAIL
password = headers_file.PASSWORD
app_id = headers_file.APP_ID


session = requests.Session()
handshake = ObtainAccessToken(session=session, userAgent=user_agent, secHeaders=login_header, email=email, password=password)


# assets_url = "https://apac.connect.nielseniq.com/discover-ui-gateway/svc/ess/asset-catalog-discovery/v3/assets"

#APAC-274039 - Caring Buyer View
#APAC-91400 - GeorgeTown Buyer View
#APAC-142243 - Caring GeorgeTown Monthly Performance
#APAC-1502771 - Caring GeorgeTown Scantrack Weekly
assets = AssetDataDB(id="APAC-91402", api_header=api_headers).get
print(assets)

export_test = ExportData(session=session, data=assets, apiHeaders=api_headers, fileName="export/testing3.xlsx", appId=app_id, userId=handshake.user_id, title="testing3")

export_test.export()




# print(len(assets))
# print(assets[0])
# formatted_json = json.dumps(test, indent=2)
# print(formatted_json)
# subprocess.run("clip", text=True, input=formatted_json)






