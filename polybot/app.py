import json
import flask
from flask import request
import os
from bot import ObjectDetectionBot
from loguru import logger
import boto3
from botocore.exceptions import ClientError

app = flask.Flask(__name__)

TELEGRAM_TOKEN="6614779870:AAFcbVMw1_KQf533k2bb1CF6zE0lafE2y9E"
region_name = "eu-west-3"
AWS_ACCESS_KEY_ID="AKIA5SPWCQVQPIYAZUWP"
AWS_SECRET_ACCESS_KEY="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"
TELEGRAM_APP_URL = "https://waseemloadbalancer-182743208.eu-west-3.elb.amazonaws.com/"
dynamodb = boto3.resource('dynamodb', region_name=region_name, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'    


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/results/', methods=['GET'])
def results():
    prediction_id = request.args.get('predictionId')
    #logger.info(f'prediction: {prediction_id}. start processing')
    # Retrieve results from DynamoDB
    table = dynamodb.Table('WaseemDynamoDBTable')

    response = table.get_item(
        Key={
            'prediction_id': prediction_id
        }
    )
    logger.info(f'results: {response}. end processing')

    chat_id = response['Item']['chat_id']
    text_results = response['Item']['labels']
    logger.info(f'chat_id :{chat_id}, text_results : {text_results}')

    bot.send_text(chat_id, text_results)
    return 'Ok results'


@app.route(f'/loadTest/', methods=['POST'])
def load_test():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    bot = ObjectDetectionBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)

    app.run(host='0.0.0.0', port=8443)
