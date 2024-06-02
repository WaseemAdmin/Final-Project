import json
import uuid
import boto3
import telebot
from botocore.exceptions import NoCredentialsError
from loguru import logger
import os
import time
from telebot.types import InputFile

TELEGRAM_TOKEN="6614779870:AAFcbVMw1_KQf533k2bb1CF6zE0lafE2y9E"
bucketS3_name = "waseembucketinstancevarginia"
sqs_queue_url = "https://sqs.eu-west-3.amazonaws.com/933060838752/WaseemAWSqueue"
region_name = "eu-west-3"
AWS_ACCESS_KEY_ID="AKIA5SPWCQVQPIYAZUWP"
AWS_SECRET_ACCESS_KEY="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"

class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)
        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        webhook_url = f'{telegram_chat_url}/{token}/'
        print(f'Setting webhook URL: {webhook_url}')
        self.telegram_bot_client.set_webhook(url=webhook_url, timeout=60, certificate=open("YOURPUBLIC.pem", 'r'))

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def set_webhook(self, telegram_chat_url):
        webhook_url = f'{telegram_chat_url}/{TELEGRAM_TOKEN}/'
        logger.info(f'Setting webhook URL: {webhook_url}')
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)
        self.telegram_bot_client.set_webhook(url=webhook_url, timeout=60)    

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class ObjectDetectionBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if 'text' in msg:
            # Send the text message back as a reply
            self.send_text(msg['chat']['id'], f'You said: {msg["text"]}')

        elif  self.is_current_msg_photo(msg):
        
            photo_path = self.download_user_photo(msg)

            # Upload the photo to S3
            logger.info(f'Photo uploaded to S3. S3 URL started : ')
            image_id = self.upload_to_s3(photo_path,bucketS3_name)


            logger.info(f'Sending the job to the sqs queue : ')
            # Send a job to the SQS queue
            message = {
                'image': image_id,
                'chat_id': msg['chat']['id']
            }
            message = json.dumps(message)
            queue_name = 'WaseemAWSqueue'
            sqs_client = boto3.client('sqs', region_name='eu-west-3')
            logger.info(f'trying get the response  ')
            response = sqs_client.send_message(QueueUrl=queue_name, MessageBody=message)
            logger.info(f'Sending to SQS ://{queue_name}/{response}')
            
            # Send a message to the Telegram end-user
            self.send_text(msg['chat']['id'], 'Your image is being processed. Please wait...')


    def upload_to_s3(self, local_path, bucketS3_name):
        logger.info(f'In upload to s3 function')
        s3 = boto3.client(
        's3',
        aws_access_key_id='AKIA5SPWCQVQPIYAZUWP',
        aws_secret_access_key='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',
        region_name='eu-west-3'
        )
        image_id = str(uuid.uuid4())
        image_id = f'{image_id}.jpeg'
        try:
            logger.info(f'Trying to upload to s3')
            s3.upload_file(local_path, bucketS3_name, image_id)
            logger.info(f'Photo uploaded to S3 Successfuly. S3 URL: s3://{bucketS3_name}/{image_id}')

            return image_id
        except Exception as e:
            logger.error(f"Error uploading photo to S3: {e}")
            return None