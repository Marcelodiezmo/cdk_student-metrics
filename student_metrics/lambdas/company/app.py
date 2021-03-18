import json
import os
import response_factory
import parquet as parquet
import dao as dao


def exception_handler(response):
    if response.error_message is None or response.error_message == '':
        response.error_message = 'General Error'

    response = response_factory.ResponseFactory.error_client(response.code, response).toJSON()
    print(response)
    return response


def build_response_body(company_info):
    print("Los datos son")
    print(company_info)

    data = (str(company_info)[1:-1]).split(',')

    mapParquet = parquet.Company(
        company_id=data[1],
        company_name=data[2],
        company_size=data[4],
        company_renewal_date=data[7],
        company_type=data[8]
    )

    return mapParquet


def handler(event, context):
    try:
        bucket = os.environ['bucket_name']
        path = 'zoho/VersionTablasDevelop2/New_company_vigencia.parquet/'

        student_id = int(event["queryStringParameters"]['studentId'])
        company_id = int(event["queryStringParameters"]['companyId'])

        # company = df.loc[df['company_id']==95, ['company_name']].to_json(orient="records")
        # company = df.loc[df['company_id']==95].to_dict('records') #No se puede pasar a JSON por el datetime.date
        df = parquet.AccessParquet().pd_read_s3_multiple_parquets(path, bucket=bucket)

        if company_id:
            company_info = df.loc[df['company_id'] == company_id].sort_values('end_date', ascending=['1']).iloc[0].to_json(orient="records")
        elif student_id:
            company_id = dao.get_company_id(student_id)
            company_info = df.loc[df['company_id'] == company_id].sort_values('end_date', ascending=['1']).iloc[0].to_json(orient="records")

        response_body = build_response_body(company_info)
        response = response_factory.ResponseFactory.ok_status(response_body).toJSON()

        print(response)
        return response
    except Exception as e:
        response = response_factory.ResponseError(404, e.args[0])
        print('ERROR: ', e.args[0])
        return exception_handler(response)
