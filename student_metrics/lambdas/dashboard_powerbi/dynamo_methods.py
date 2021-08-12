import boto3

dynamo_client = boto3.client('dynamodb')

class Dynamo_Methods:
    def get_credentials_from_dynamo(self, environment):
        try:
            table_name = 'powerbiCredentials'
            response = dynamo_client.get_item(
                TableName=table_name,
                Key={
                    'environment': {'S': environment}
                }
            )
            return response
        except:
            return None

    def get_value_from_powerbi_data(self, type_value):
        try:
            table_name = 'powerbiData'
            response = dynamo_client.get_item(
                TableName=table_name,
                Key={
                    'type': {'S': type_value}
                }
            )
            return response
        except:
            return None

    def write_dynamo_data(type_value, value):
        try:
            response = dynamo_client.put_item(
                TableName='powerbiData',
                Item = {
                    'type': {"S": type_value},
                    'value': {"S": value}
                }
            )
            return response
        except:
            return None
