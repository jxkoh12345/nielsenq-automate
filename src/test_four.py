import sqlite3
import time
import requests
from get_asset_data import GetAssetData
import headers_file
from oie_login import ObtainAccessToken
from save_asset_data import AssetDataDB

user_agent = headers_file.USER_AGENT
api_headers = headers_file.API_HEADERS
login_header = headers_file.LOGIN_HEADERS
email = headers_file.EMAIL
password = headers_file.PASSWORD


session = requests.Session()
handshake = ObtainAccessToken(session=session, userAgent=user_agent, secHeaders=login_header, email=email, password=password)


def check_for_new_assets(db:sqlite3, db_assets):
    """
    Check for new assets
    """
    to_be_insert_asset_data = []
    for asset in assets:
        if asset["assetId"] not in db_assets:
            to_be_insert_asset_data.append(asset)
    
    if(len(to_be_insert_asset_data) > 0):
        db.bulk_insert_into_table(to_be_insert_asset_data)   




def check_for_updated_date(db:sqlite3, dict_list_date):
    """
    Check for updated date
    """
    to_be_insert_asset_data = []
    for asset in assets:
        if dict_list_date[asset["assetId"]] != asset["lastModified"]:
            print(f"Ori: {dict_list_date[asset["assetId"]]} --> New: {asset["lastModified"]}")
            to_be_insert_asset_data.append(asset)
    
    if(len(to_be_insert_asset_data) > 0):
        db.bulk_insert_into_table(to_be_insert_asset_data)
    


if __name__ == "__main__":

    #APAC-238158 - Caring Buyer View
    #APAC-91400 - GeorgeTown Buyer View
    assets = GetAssetData(session=session, id="APAC-238158", api_header=api_headers).get
 
    with AssetDataDB("db/assets.db") as db:

        # list = db.get_asset_id_by_parents(id="APAC-91400")
        # db_assets = [data[0] for data in list]

        # list_date = db.get_asset_id_and_modified_date_by_parents(id="APAC-91400")
        # dict_list_date = dict(list_date)
        db.bulk_insert_into_table(assets)
