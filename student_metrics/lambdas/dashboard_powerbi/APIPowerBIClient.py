import requests
import json
import msal

# Can be set to 'MasterUser' or 'ServicePrincipal'
AUTHENTICATION_MODE = 'ServicePrincipal'

# Workspace Id in which the report is present
WORKSPACE_ID = '54231e4b-5621-4453-a4e6-e3d996fbec9c'

# Report Id for which Embed token needs to be generated
REPORT_ID = 'a74fff32-9316-411c-83c7-37fbe9a542c7'

# Id of the Azure tenant in which AAD app and Power BI report is hosted. Required only for ServicePrincipal authentication mode.
TENANT_ID = 'a0773bda-3c38-41c9-9529-13b2db7a3826'

# Client Id (Application Id) of the AAD app
CLIENT_ID = '4cc96646-cb74-4aca-a6c7-85fce1c0154f'

# Client Secret (App Secret) of the AAD app. Required only for ServicePrincipal authentication mode.
CLIENT_SECRET = 'ViD1a.UFiMizD6-a7R7duBU98~_D3HhZ.L'

# Scope of AAD app. Use the below configuration to use all the permissions provided in the AAD app through Azure portal.
SCOPE = 'https://analysis.windows.net/powerbi/api/.default'

# URL used for initiating authorization request
AUTHORITY = 'https://login.microsoftonline.com/organizations'

# Master user email address. Required only for MasterUser authentication mode.
POWER_BI_USER = 'tech@ubits.co'

# Master user email password. Required only for MasterUser authentication mode.
POWER_BI_PASS = 'Ubits+123'


# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license
class EmbedConfig:
    # Camel casing is used for the member variables as they are going to be serialized and camel case is standard for JSON keys
    tokenId = None
    accessToken = None
    tokenExpiry = None
    reportConfig = None

    # filters = None
    def __init__(self, token_id, access_token, token_expiry, report_config):
        self.tokenId = token_id
        self.accessToken = access_token
        self.tokenExpiry = token_expiry
        self.reportConfig = report_config
        # self.filters = filters


# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license
class EmbedToken:
    # Camel casing is used for the member variables as they are going to be serialized and camel case is standard for JSON keys
    tokenId = None
    token = None
    tokenExpiry = None

    def __init__(self, token_id, token, token_expiry):
        self.tokenId = token_id
        self.token = token
        self.tokenExpiry = token_expiry


# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license
class EmbedTokenRequestBody:
    # Camel casing is used for the member variables as they are going to be serialized and camel case is standard for JSON keys
    datasets = None
    reports = None
    targetWorkspaces = None

    def __init__(self):
        self.datasets = []
        self.reports = []
        self.targetWorkspaces = []


# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license
class ReportConfig:
    # Camel casing is used for the member variables as they are going to be serialized and camel case is standard for JSON keys
    reportId = None
    reportName = None
    embedUrl = None
    datasetId = None

    def __init__(self, report_id, report_name, embed_url, dataset_id=None):
        self.reportId = report_id
        self.reportName = report_name
        self.embedUrl = embed_url
        self.datasetId = dataset_id


class PowerBIClientService:

    header = None

    def __init__(self):
        print("Constructor")
        self.header = self.getHeader(self)

    @staticmethod
    def getHeader(self):
        print("Get Header for client ")
        authority = AUTHORITY.replace('organizations', TENANT_ID)
        clientapp = msal.ConfidentialClientApplication(CLIENT_ID, client_credential=CLIENT_SECRET, authority=authority)
        # Make a client call if Access token is not available in cache
        response = clientapp.acquire_token_for_client(scopes=SCOPE)
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + response['access_token']}

        print(header)
        return header

    def getURLDashboard(self):
        print("Get URL Dashboard")

        report_url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}"
        #report_url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}?filter=user_full/company_name eq 'UBITS - Cliente'"
        api_response = requests.get(report_url, headers=self.header)

        api_response = json.loads(api_response.text)
        report = ReportConfig(api_response['id'], api_response['name'], api_response['embedUrl'])

        dataset_ids = [api_response['datasetId']]
        request_body = EmbedTokenRequestBody()
        request_body.datasets.append({'id': dataset_ids})
        request_body.reports.append({'id': REPORT_ID})
        request_body.targetWorkspaces.append({'id': WORKSPACE_ID})

        embed_token_api = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}/GenerateToken"
        api_response = requests.post(embed_token_api, data=json.dumps(request_body.__dict__), headers=self.header)
        print(api_response.status_code)

        if api_response.status_code == "200":
            api_response = json.loads(api_response.text)
            embed_token = EmbedToken(api_response['tokenId'], api_response['token'], api_response['expiration'])
            embed_config = EmbedConfig(embed_token.tokenId, embed_token.token, embed_token.tokenExpiry, [report.__dict__])

            response = embed_config.__dict__
            print(response['reportConfig'][0]['reportName'])
            return response
        else:
            print("ERROR: ", "Error consuming the PowerBI API")
            raise Exception("Error consuming the PowerBI API")