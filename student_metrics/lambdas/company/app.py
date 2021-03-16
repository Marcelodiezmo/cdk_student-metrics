import json
import os
import pandas as pd
import boto3
import io


s3 = boto3.client('s3')

# Read single parquet file from S3
def pd_read_s3_parquet(key, bucket, **args):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_parquet(io.BytesIO(obj['Body'].read()), **args)

def pd_read_s3_multiple_parquets(filepath, bucket, **args):
    if not filepath.endswith('/'):
        filepath = filepath + '/'

    s3 = boto3.resource('s3')
    s3_keys = [item.key for item in s3.Bucket(bucket).objects.filter(Prefix=filepath)
               if item.key.endswith('.parquet')]

    if not s3_keys:
        print('No parquet found in', bucket, filepath)

    dfs = [pd_read_s3_parquet(key, bucket=bucket, **args)
           for key in s3_keys]
    return pd.concat(dfs, ignore_index=True)

def handler(event, context):
    bucket = os.environ['bucket_name']
    path = 'zoho/VersionTablasDevelop2/New_company_vigencia.parquet/'
    companyId = int(event['pathParameters']['companyid'])

    df = pd_read_s3_multiple_parquets(path, bucket=bucket)
    # company = df.loc[df['company_id']==95, ['company_name']].to_json(orient="records")

    # company = df.loc[df['company_id']==95].to_dict('records') #No se puede pasar a JSON por el datetime.date
    company = df.loc[df['company_id']==95].to_json(orient="records")
    print("El resultado es")
    print(company)
