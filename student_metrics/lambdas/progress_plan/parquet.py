import pandas as pd
import io
import boto3

s3 = boto3.client('s3')

class AccessParquet:
    ERROR_MESSAGE = 'No parquet found in {} {}'

    # Read single parquet file from S3
    @staticmethod
    def pd_read_s3_parquet(key, bucket, **args):
        obj = s3.get_object(Bucket=bucket, Key=key)
        return pd.read_parquet(io.BytesIO(obj['Body'].read()), **args)

    def pd_read_s3_multiple_parquets(self, filepath, bucket, **args):
        if not filepath.endswith('/'):
            filepath = filepath + '/'

        s3 = boto3.resource('s3')
        s3_keys = [item.key for item in s3.Bucket(bucket).objects.filter(Prefix=filepath)
                   if item.key.endswith('.parquet')]

        if not s3_keys:
            msg = self.ERROR_MESSAGE.format(bucket, filepath)
            print(msg)
            raise Exception(msg)

        dfs = [self.pd_read_s3_parquet(key, bucket=bucket, **args)
               for key in s3_keys]
        return pd.concat(dfs, ignore_index=True)
