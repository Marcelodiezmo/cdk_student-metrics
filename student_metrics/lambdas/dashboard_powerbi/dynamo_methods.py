import boto3

from constants import TABLE_CREDENTIALS, TABLE_DATA 

dynamo_client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

class Dynamo_Methods:
    def get_credentials_from_dynamo(environment):
        table = dynamodb.Table(TABLE_CREDENTIALS)

        try:
            response = table.get_item(
            Key={
                    'environment': environment
                }
            )
            return response['Item']
        except Exception as e:
            print(e)
            return None

    def get_value_from_powerbi_data(type_value):
        table = dynamodb.Table(TABLE_DATA)

        try:
            response = table.get_item(
            Key={
                    'type': type_value
                }
            )
            return response['Item']
        except Exception as e:
            print(e)
            return None

    def write_dynamo_data(type_value, value):
        try:
            response = dynamo_client.put_item(
                TableName=TABLE_DATA,
                Item = {
                    'type': {"S": type_value},
                    'value': {"S": value}
                }
            )
            return response
        except Exception as e:
            print(e)
            return None
