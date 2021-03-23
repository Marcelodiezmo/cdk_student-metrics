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


def getParam(event, param_name):
    try:
        return int(event["queryStringParameters"][param_name])
    except:
        return 0

def build_response_body(company_info):
    company_id = str(company_info['company_id'])
    company_name = str(company_info['company_name'])
    company_size = str(company_info['licencias'])
    company_renewal_date = str(company_info['end_date'])
    company_type = str(company_info['Tamaño_Licencias'])

    mapParquet = parquet.Company(
        company_id=company_id,
        company_name=company_name,
        company_size=company_size,
        company_renewal_date=company_renewal_date,
        company_type=company_type
    )

    return mapParquet


def handler(event, context):
    try:
        bucket = 'analytics-ubits-production-dev'
        path = 'zoho/VersionTablasDevelop2/New_company_vigencia.parquet/'

        student_id = getParam(event, 'studentid')
        company_id = getParam(event, 'companyid')

        # company = df.loc[df['company_id']==95, ['company_name']].to_json(orient="records")
        # company = df.loc[df['company_id']==95].to_dict('records') #No se puede pasar a JSON por el datetime.date

        # df = parquet.AccessParquet().pd_read_s3_multiple_parquets(path, bucket=bucket)

        if company_id != 0:
            df = parquet.AccessParquet().pd_read_s3_multiple_parquets(path, bucket=bucket, columns=['company_id','company_name','licencias','Tamaño_Licencias','end_date'],filters=[('company_id','=',company_id)])
            # search_company = df.loc[df['company_id'] == company_id].sort_values('end_date', ascending=['1'])
        elif student_id != 0:
            company_id = dao.get_company_id(student_id)
            df = parquet.AccessParquet().pd_read_s3_multiple_parquets(path, bucket=bucket, columns=['company_id','company_name','licencias','Tamaño_Licencias','end_date'],filters=[('company_id','=',int(company_id))])
            # search_company = df.loc[df['company_id'] == company_id].sort_values('end_date', ascending=['1'])
        else:
            raise Exception("Necessary Filters")

        if not df.empty:
            search_company = df.sort_values('end_date', ascending=['1'])
        else:
            raise Exception("No company found")

        if not search_company.empty:
            company_info = search_company.iloc[0].to_dict()
            response_body = build_response_body(company_info)
            response = response_factory.ResponseFactory.ok_status(response_body).toJSON()
            return response
        else:
            raise Exception('No company found')
    except Exception as e:
        response = response_factory.ResponseError(404, e.args[0])
        print('ERROR: ', e.args[0])
        return exception_handler(response)
