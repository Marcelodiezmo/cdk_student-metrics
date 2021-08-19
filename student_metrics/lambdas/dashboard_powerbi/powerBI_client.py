import requests, datetime, json, msal
from tzlocal import get_localzone

from dynamo_methods import Dynamo_Methods
from send_email import Send_Email
from constants import MAIN_DYNAMO_CREDENTIALS, BACKUP_DYNAMO_CREDENTIALS, USERNAME_SMTP, PASSWORD_SMTP, CONFIGURATION_SET, SENDER, SENDER_NAME

AUTHORITY = ""
CREDENTIALS = { 
    "TENANT_ID": "",
    "CLIENT_ID": "",
    "CLIENT_SECRET": "",
    "SCOPE": "",
    "WORKSPACE_ID": "",
    "REPORT_ID": ""
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
    
    def checkTokenTime(self, tokenExpiry):
        tokenExpiry = datetime.datetime.strptime(tokenExpiry, "%Y-%m-%dT%H:%M:%S%z")
        timeLeft = tokenExpiry.astimezone(get_localzone()) - datetime.datetime.now().astimezone(get_localzone())
        if timeLeft.total_seconds() > 60: return True
        else: return False

    def write_in_dynamo(self, type_value, value):
        response = Dynamo_Methods.write_dynamo_data(type_value = type_value, value = value)
        return response

    def get_credentials_from_dynamo(self, credentials):
        dynamo_credentials = Dynamo_Methods.get_credentials_from_dynamo(credentials)

        if dynamo_credentials:
            global CREDENTIALS
            CREDENTIALS.update(
                {
                    "TENANT_ID": dynamo_credentials.get("tenantId"),
                    "CLIENT_ID": dynamo_credentials.get("clientId"),
                    "CLIENT_SECRET": dynamo_credentials.get("clientSecret"),
                    "SCOPE": dynamo_credentials.get("scope"),
                    "WORKSPACE_ID": dynamo_credentials.get("workspaceId"),
                    "REPORT_ID": dynamo_credentials.get("reportId"),
                })
            global AUTHORITY
            AUTHORITY = dynamo_credentials.get("authorityUri")

    def get_value_from_dynamo(self, type_value):
        value_dynamo = Dynamo_Methods.get_value_from_powerbi_data(type_value=type_value)

        if value_dynamo:
            return value_dynamo.get("value")
        else:
            return None

    # Get header with JWT Token
    def get_header(self, search_dynamo: False, credentials: None):
        self.get_credentials_from_dynamo(credentials if credentials else MAIN_DYNAMO_CREDENTIALS)
        header_dynamo = None

        if search_dynamo:
            header_dynamo = self.get_value_from_dynamo('header')

        # Find some header from dynamo
        if header_dynamo:
            return json.loads(header_dynamo.replace("'",'"'))
        else:
            return self.generate_header()

    
    def get_token(self, new_token: False):
        token_dynamo = None

        if not new_token:
            token_dynamo = self.get_value_from_dynamo('token')
            report_dynamo = self.get_value_from_dynamo('report')
        
        # Find token from dynamo
        if token_dynamo:
            report_dict = eval(report_dynamo)
            response_token = json.loads(token_dynamo.replace("'",'"'))
            report = ReportConfig(report_dict.get('reportId'), report_dict.get('reportName'), report_dict.get('embedUrl'))
            embed_token = EmbedToken(response_token['tokenId'], response_token['token'], response_token['expiration'])
            embed_config = EmbedConfig(embed_token.tokenId, embed_token.token, embed_token.tokenExpiry, [report.__dict__])
            
            if self.checkTokenTime(response_token['expiration']):
                return embed_config
            else:
                self.header = self.get_header(search_dynamo = True, credentials = None)
                return self.get_dashboard_url()

        else:
            # Search the header from dynamo or create a new header
            self.header = self.get_header(search_dynamo = True, credentials = None)
        
        return self.get_dashboard_url()
        
    
    def generate_header(self):
        authority = AUTHORITY.replace('organizations', CREDENTIALS.get("TENANT_ID"))
        clientapp = msal.ConfidentialClientApplication(CREDENTIALS.get("CLIENT_ID"), client_credential=CREDENTIALS.get("CLIENT_SECRET"), authority=authority)

        # Make a client call if Access token is not available in cache
        response = clientapp.acquire_token_for_client(scopes=CREDENTIALS.get("SCOPE"))
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + response['access_token']}

        self.write_in_dynamo(type_value='header', value=str(header))
        return header
    
    def control_exception_token(self):
        global DYNAMO_CREDENTIALS
        if DYNAMO_CREDENTIALS == "":
            DYNAMO_CREDENTIALS = BACKUP_DYNAMO_CREDENTIALS
            self.header = self.get_header(search_dynamo = False, credentials = BACKUP_DYNAMO_CREDENTIALS)
            return self.get_dashboard_url()
        else:
            Send_Email.email_powerbi_notify(sender=SENDER, sender_name=SENDER_NAME, recipient='rgarcia@ubits.co', username_smtp=USERNAME_SMTP, password_smtp=PASSWORD_SMTP, configuration_set=CONFIGURATION_SET, last_header=self.header, CREDENTIALS=CREDENTIALS, api_response="404 Error")
            raise Exception(404, "Error consuming the PowerBI API")

    def validate_response_report(self, response_report):
        if response_report.status_code == 200:
            report_data = response_report.json()
            report = ReportConfig(report_data['id'], report_data['name'], report_data['embedUrl'])

            request_body = EmbedTokenRequestBody()
            request_body.datasets.append({'id': [report_data['datasetId']]})
            request_body.reports.append({'id': CREDENTIALS.get("REPORT_ID")})
            request_body.targetWorkspaces.append({'id': CREDENTIALS.get("WORKSPACE_ID")})

            embed_token_api = f"https://api.powerbi.com/v1.0/myorg/groups/{CREDENTIALS.get('WORKSPACE_ID')}/reports/{CREDENTIALS.get('REPORT_ID')}/GenerateToken"
            response_token = requests.post(embed_token_api, data=json.dumps(request_body.__dict__), headers=self.header)

            return self.validate_response_token(response_token, report)
        else:
            return self.control_exception_token()
        

    def validate_response_token(self, response_token, report):
        if response_token.status_code == 200:
            response_token = response_token.json()
            embed_token = EmbedToken(response_token['tokenId'], response_token['token'], response_token['expiration'])
            embed_config = EmbedConfig(embed_token.tokenId, embed_token.token, embed_token.tokenExpiry, [report.__dict__])

            self.write_in_dynamo(type_value='report', value=str(report.__dict__))
            self.write_in_dynamo(type_value='token', value=str(response_token))
            return embed_config
        else:
            return self.control_exception_token()
    
    
    # Get the dashboard data
    def get_dashboard_url(self):
        report_url = f"https://api.powerbi.com/v1.0/myorg/groups/{CREDENTIALS.get('WORKSPACE_ID')}/reports/{CREDENTIALS.get('REPORT_ID')}"
        response_report = requests.get(report_url, headers=self.header)

        return self.validate_response_report(response_report)