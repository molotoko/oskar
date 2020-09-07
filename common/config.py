import os
from boto.s3.connection import S3Connection

telegram_api_key = os.environ['TELEGRAM_API_KEY']
bot_name = os.environ['BOT_NAME']

s3 = S3Connection(telegram_api_key, bot_name)
