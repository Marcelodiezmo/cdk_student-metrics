import boto3

dynamo_client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

class Dynamo_Methods:
    def get_credentials_from_dynamo(environment):
        print("El environment es ", environment)

        table = dynamodb.Table('powerbiCredentials')

        try:
            response = table.get_item(
            Key={
                    'environment': environment
                }
            )
            print("La respuesta es")
            print(response['Item'])
            return response['Item']
        except Exception as e:
            print(e)
            return None

    def get_value_from_powerbi_data(type_value):
        print("metodo get_value_from_powerbi_data")

        table = dynamodb.Table('powerbiData')

        try:
            response = table.get_item(
            Key={
                    'type': type_value
                }
            )
            print("La respuesta es")
            print(response['Item'])
            return response['Item']
        except Exception as e:
            print(e)
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
        except Exception as e:
            print(e)
            return None
