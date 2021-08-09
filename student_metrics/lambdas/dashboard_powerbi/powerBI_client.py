import requests
import json
import msal
import os
import boto3

dynamo_client = boto3.client('dynamodb')

# Can be set to 'MasterUser' or 'ServicePrincipal'
AUTHENTICATION_MODE = 'ServicePrincipal'

# Workspace Id in which the report is present
WORKSPACE_ID = os.environ['WORKSPACE_ID']

# Report Id for which Embed token needs to be generated
REPORT_ID = os.environ['REPORT_ID']

# Id of the Azure tenant in which AAD app and Power BI report is hosted. Required only for ServicePrincipal
# authentication mode.
TENANT_ID = os.environ['TENANT_ID']

# Client Id (Application Id) of the AAD app
CLIENT_ID = os.environ['CLIENT_ID']

# Client Secret (App Secret) of the AAD app. Required only for ServicePrincipal authentication mode.
CLIENT_SECRET = os.environ['CLIENT_SECRET']

# Scope of AAD app. Use the below configuration to use all the permissions provided in the AAD app through Azure portal.
SCOPE = 'https://analysis.windows.net/powerbi/api/.default'

# URL used for initiating authorization request
AUTHORITY = 'https://login.microsoftonline.com/organizations'

# Master user email address. Required only for MasterUser authentication mode.
POWER_BI_USER = os.environ['POWER_BI_USER']

# Master user email password. Required only for MasterUser authentication mode.
POWER_BI_PASS = os.environ['POWER_BI_PASS']


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
        self.header = self.get_header(self)

    # Get header with JWT Token
    @staticmethod
    def get_header(self):
        print("Get Header for client")
        authority = AUTHORITY.replace('organizations', TENANT_ID)
        clientapp = msal.ConfidentialClientApplication(CLIENT_ID, client_credential=CLIENT_SECRET, authority=authority)

        # Make a client call if Access token is not available in cache
        response = clientapp.acquire_token_for_client(scopes=SCOPE)
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + response['access_token']}

        return header

    def get_credentials_from_dynamo(self, environment):
        table_name = 'powerbiCredentials'
        response = dynamo_client.get_item(
            TableName=table_name,
            Key={
                'environment': {'S': environment}
            }
        )

        return response

    # TODO: Crear metodo para obtener header de dynamo

    # TODO: Crear metodo para guardar header en dynamo

    # Get the dashboard data
    def get_dashboard_url(self):
        print("Get URL Dashboard")

        # Get report data
        report_url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}"
        #report_url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}?filter=user_full/company_name eq 'UBITS - Cliente'"
        response_report = requests.get(report_url, headers=self.header)

        if response_report.status_code != 200:
            print("ERROR: ", response_report.status_code, response_report.json()["error"]["code"])
            raise Exception(response_report.status_code, response_report.json()["error"]["code"])

        report_data = response_report.json()
        report = ReportConfig(report_data['id'], report_data['name'], report_data['embedUrl'])

        request_body = EmbedTokenRequestBody()
        request_body.datasets.append({'id': [report_data['datasetId']]})
        request_body.reports.append({'id': REPORT_ID})
        request_body.targetWorkspaces.append({'id': WORKSPACE_ID})

        # Get token for dashboard
        embed_token_api = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/reports/{REPORT_ID}/GenerateToken"
        response_token = requests.post(embed_token_api, data=json.dumps(request_body.__dict__), headers=self.header)
        print(response_token.status_code)

        if response_token.status_code == 200:
            response_token = response_token.json()
            embed_token = EmbedToken(response_token['tokenId'], response_token['token'], response_token['expiration'])
            embed_config = EmbedConfig(embed_token.tokenId, embed_token.token, embed_token.tokenExpiry, [report.__dict__])

            print(embed_config)
            return embed_config
        else:
            print("ERROR: ", "Error consuming the PowerBI API")
            raise Exception(404, "Error consuming the PowerBI API")