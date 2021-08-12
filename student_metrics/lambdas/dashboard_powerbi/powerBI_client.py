import requests
import json
import msal
from dynamo_methods import Dynamo_Methods
from constants import WORKSPACE_ID, REPORT_ID, TENANT_ID, CLIENT_ID, CLIENT_SECRET, SCOPE, AUTHORITY, MAIN_DYNAMO_CREDENTIALS, BACKUP_DYNAMO_CREDENTIALS

CREDENTIALS = { 
    "TENANT_ID": TENANT_ID,
    "CLIENT_ID": CLIENT_ID,
    "CLIENT_SECRET": CLIENT_SECRET,
    "SCOPE": SCOPE,
    "WORKSPACE_ID": WORKSPACE_ID,
    "REPORT_ID": REPORT_ID
}

DYNAMO_CREDENTIALS = ""

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license
class EmbedConfig:
    # Camel casing is used for the member variables as they are going to be serialized and camel case is standard for
    # JSON keys
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
    # Camel casing is used for the member variables as they are going to be serialized and camel case is standard for
    # JSON keys
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
    # Camel casing is used for the member variables as they are going to be serialized and camel case is standard for
    # JSON keys
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
    # Camel casing is used for the member variables as they are going to be serialized and camel case is standard for
    # JSON keys
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
        # self.header = self.get_header(self)

    def get_credentials_from_dynamo(credentials):
        dynamo_credentials = Dynamo_Methods.get_credentials_from_dynamo(credentials)
        
        if dynamo_credentials:
            global CREDENTIALS
            CREDENTIALS.update(
                {
                    "TENANT_ID": dynamo_credentials.TENANT_ID,
                    "CLIENT_ID": dynamo_credentials.CLIENT_ID,
                    "CLIENT_SECRET": dynamo_credentials.CLIENT_SECRET,
                    "SCOPE": dynamo_credentials.SCOPE,
                    "WORKSPACE_ID": dynamo_credentials.WORKSPACE_ID,
                    "REPORT_ID": dynamo_credentials.REPORT_ID,
                })

    def get_value_from_dynamo(type_value):
        value_dynamo = Dynamo_Methods.get_value_from_powerbi_data(type_value)

        if value_dynamo:
            return value_dynamo
        else:
            return None

    # Get header with JWT Token
    def get_header(self, search_dynamo: False, credentials: None):
        header_dynamo = None

        if search_dynamo:
            header_dynamo = self.get_value_from_dynamo('header')

        # Find some header from dynamo
        if header_dynamo:
            return header_dynamo
        else:
            self.get_credentials_from_dynamo(credentials if credentials else MAIN_DYNAMO_CREDENTIALS)
            return self.generate_header()

    
    def get_token(self, new_token: False):
        token_dynamo = None

        if not new_token:
            token_dynamo = self.get_value_from_dynamo('token')

        # Find token from dynamo
        if token_dynamo:
            # TODO: Validar la fecha de expiracion del token
            return token_dynamo
        else:
            # Search the header from dynamo or create a new header
            self.header = self.get_header(search_dynamo = True)
        
        return self.get_dashboard_url()
        
    
    def generate_header(self):
        authority = AUTHORITY.replace('organizations', CREDENTIALS.GET("TENANT_ID"))
        clientapp = msal.ConfidentialClientApplication(CREDENTIALS.GET("CLIENT_ID"), client_credential=CREDENTIALS.GET("CLIENT_SECRET"), authority=authority)

        # Make a client call if Access token is not available in cache
        response = clientapp.acquire_token_for_client(scopes=CREDENTIALS.GET("SCOPE"))
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + response['access_token']}

        # TODO: Save header in dynamo
        return header
    
    def validate_response_token(self, response_token, report):
        if response_token.status_code == 200:
            response_token = response_token.json()
            embed_token = EmbedToken(response_token['tokenId'], response_token['token'], response_token['expiration'])
            embed_config = EmbedConfig(embed_token.tokenId, embed_token.token, embed_token.tokenExpiry, [report.__dict__])

            # TODO: Save token in dynamo. Save expiration time in dynamo
            print(embed_config)
            return embed_config
        else:
            print(f"DYNAMO_CREDENTIALS = {DYNAMO_CREDENTIALS}")
            if DYNAMO_CREDENTIALS == "":
                global DYNAMO_CREDENTIALS
                DYNAMO_CREDENTIALS = BACKUP_DYNAMO_CREDENTIALS
                self.header = self.get_header(search_dynamo = False, credentials = BACKUP_DYNAMO_CREDENTIALS)

                return self.get_dashboard_url()
            else:
                print("Enviar correo")
    
    
    # Get the dashboard data
    def get_dashboard_url(self):
        print("Get URL Dashboard")

        # Get report data
        report_url = f"https://api.powerbi.com/v1.0/myorg/groups/{CREDENTIALS.GET('WORKSPACE_ID')}/reports/{CREDENTIALS.GET('REPORT_ID')}"
        #report_url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}?filter=user_full/company_name eq 'UBITS - Cliente'"
        response_report = requests.get(report_url, headers=self.header)

        if response_report.status_code != 200:
            print("ERROR: ", response_report.status_code, response_report.json()["error"]["code"])
            raise Exception(response_report.status_code, response_report.json()["error"]["code"])

        report_data = response_report.json()
        report = ReportConfig(report_data['id'], report_data['name'], report_data['embedUrl'])

        request_body = EmbedTokenRequestBody()
        request_body.datasets.append({'id': [report_data['datasetId']]})
        request_body.reports.append({'id': CREDENTIALS.GET("REPORT_ID")})
        request_body.targetWorkspaces.append({'id': CREDENTIALS.GET("WORKSPACE_ID")})

        # Get token for dashboard
        embed_token_api = f"https://api.powerbi.com/v1.0/myorg/groups/{CREDENTIALS.GET('WORKSPACE_ID')}/reports/{CREDENTIALS.GET('REPORT_ID')}/GenerateToken"
        response_token = requests.post(embed_token_api, data=json.dumps(request_body.__dict__), headers=self.header)
        print(response_token.status_code)

        return self.validate_response_token(response_token, report)
        
        # if response_token.status_code == 200:
        #     response_token = response_token.json()
        #     embed_token = EmbedToken(response_token['tokenId'], response_token['token'], response_token['expiration'])
        #     embed_config = EmbedConfig(embed_token.tokenId, embed_token.token, embed_token.tokenExpiry, [report.__dict__])

        #     print(embed_config)
        #     return embed_config
        # else:
        #     print("ERROR: ", "Error consuming the PowerBI API")
        #     raise Exception(404, "Error consuming the PowerBI API")