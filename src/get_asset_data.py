import requests



class GetAssetData:

    def __init__(self, session:requests.Session, api_header, id=""):
        self.session = session
        self.assets_url = "https://apac.connect.nielseniq.com/discover-ui-gateway/svc/ess/asset-catalog-discovery/v3/assets"

        self.payload = self.set_payload(id)
        self.get = self.getAssetData(self.assets_url, self.payload, api_header)

#APAC-274039 - Caring Buyer View
#APAC-91400 - GeorgeTown Buyer View

    def set_payload(self, id):

        payload = {
            "properties": {
                "displayAllRights": True,
                "filterElements": True,
                "assetElements": True,
                "userTags": True,
                "sourceId": True,
                "timezone": "Asia/Kuala_Lumpur",
                "pageCount": 100,
                "pageNumber": "",
                "dateSortType": "MODIFIED",
                "fetchScheduledInfo": True,
                "parentAsset": True,
                "showImmediateChildren": True
            },
            "assets": [
                {
                    "status": "OPEN"
                },
                {
                    "status": "SCHEDULED"
                },
                {
                    "assetType": "DISCOVERREPORT"
                },
                {
                    "assetType": "DISCOVERGUIDEDFLOW"
                },
                {
                    "assetType": "DISCOVERFOLDER"
                },
                {
                    "assetType": "DISCOVERSHAREDFOLDER"
                },
                {
                    "assetType": "DISCOVERREPORTTEMPLATE"
                },
                {
                    "assetType": "DISCOVERGUIDEDFLOWTEMPLATE"
                },
                {
                    "assetType": "DISCOVERSNAPSHOT"
                },
                {
                    "assetType": "DISCOVERSNAPSHOTGUIDEDFLOW"
                },
            ],
            "filters": [
                {
                    "typeKey": "AVL",
                    "exclusions": [
                        {
                            "availability": "PUBLISHED"
                        }
                    ],
                    "elements": [
                        {
                            "availability": "EDIT"
                        },
                        {
                            "availability": "VIEW"
                        },
                        {
                            "availability": "STRICTVIEW"
                        },
                        {
                            "availability": "OWNED"
                        }
                    ]
                },
                {
                    "typeKey": "HIER",
                    "elements": [
                        {
                            "id": id
                            # "id": "APAC-238158"
                        }
                    ]
                }
            ],
            "sort": {
                "primarySort": "DATE",
                "sortOrder": "DESC"
            },
            "datasets": []
        }
    
        return payload



    def getAssetData(self, url, payload, api_header) -> list:
        raw_data = self.session.post(url=url, json=payload, headers=api_header)
        asset_data = raw_data.json()["data"]["assets"]
        # print([item["title"] for item in asset_data])
        return asset_data



