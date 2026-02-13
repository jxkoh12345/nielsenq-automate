import json
import requests
import subprocess
import headers_file
from oie_login import ObtainAccessToken
from get_asset_data import GetAssetData
from save_asset_data import AssetDataDB

user_agent = headers_file.USER_AGENT
api_headers = headers_file.API_HEADERS
login_header = headers_file.LOGIN_HEADERS
email = headers_file.EMAIL
password = headers_file.PASSWORD


session = requests.Session()
handshake = ObtainAccessToken(session=session, userAgent=user_agent, secHeaders=login_header, email=email, password=password)


# assets_url = "https://apac.connect.nielseniq.com/discover-ui-gateway/svc/ess/asset-catalog-discovery/v3/assets"

#APAC-274039 - Caring Buyer View
#APAC-91400 - GeorgeTown Buyer View
assets = GetAssetData(session=session, id="APAC-274039", api_header=api_headers).get
# print(assets)
# print(assets)
db = AssetDataDB(db_path="db/assets.db")
db.bulk_insert_into_table(asset_data=assets)
db.__exit__()

# formatted_json = json.dumps(html.json(), indent=2)
# print(formatted_json)
# subprocess.run("clip", text=True, input=formatted_json)




