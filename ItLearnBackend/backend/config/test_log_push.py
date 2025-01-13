import logging
import watchtower
from django.http import JsonResponse
import boto3
from decouple import config

def test_logging(request):
    logger = logging.getLogger('django_watchtower_test')
    logger.setLevel(logging.DEBUG)

    handler = watchtower.CloudWatchLogHandler(
        log_group='/courses-it-logs-group',
        stream_name='manual-test-log-stream',
        boto3_client=boto3.client(
            'logs',
            aws_access_key_id=config('AWS_ACCESS_KEY', cast=str, default=None),
            aws_secret_access_key=config('AWS_SECRET_KEY', cast=str, default=None),
            region_name='us-east-1'
        )
    )
    logger.addHandler(handler)

    logger.info("Testing logging from Django!")
    return JsonResponse({'message': 'Logged to CloudWatch!'})

def test_default_logger(request):
    logger = logging.getLogger('default')
    logger.info("Testing default logger!")
    return JsonResponse({'message': 'Default logger test complete!'})
