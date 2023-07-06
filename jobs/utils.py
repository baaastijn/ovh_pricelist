import ssl
import os
import boto3
import gzip
import json
import urllib.request

ssl._create_default_https_context = ssl._create_unverified_context

SUBSIDIARIES = ['CZ','DE','ES','FI','FR','GB','IE','IT','LT','MA','NL','PL','PT','SN','TN']
S3_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID')
S3_SECRET_ACCESS_KEY = os.getenv('S3_SECRET_ACCESS_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')


def s3():
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#examples
    return boto3.client(
            "s3",
            endpoint_url="https://s3.gra.io.cloud.ovh.net/",
            region_name='gra',
            aws_access_key_id=S3_ACCESS_KEY_ID,
            aws_secret_access_key=S3_SECRET_ACCESS_KEY,
        )

def upload_json(jsonObject, filename, bucket):
    return s3().put_object(Body=json.dumps(jsonObject), Bucket=bucket, Key=filename, ContentType='application/json', ACL='public-read')


def upload_gzip_json(jsonObject, filename, bucket):
    body = gzip.compress(bytes(json.dumps(jsonObject), encoding='utf-8'))
    return s3().put_object(Body=body, Bucket=bucket, Key=filename, ContentType='application/json', ContentEncoding='gzip', ACL='public-read')


def get_json(url):
    req = urllib.request.Request(url, headers={'Accept': 'application/json'}) 
    return json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
