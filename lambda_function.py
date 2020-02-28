"""This function handles a Slack slash command and echoes the details back to the user.

Follow these steps to configure the slash command in Slack:

  1. Navigate to https://<your-team-domain>.slack.com/services/new

  2. Search for and select "Slash Commands".

  3. Enter a name for your command and click "Add Slash Command Integration".

  4. Copy the token string from the integration settings and use it in the next section.

  5. After you complete this blueprint, enter the provided API endpoint URL in the URL field.


To encrypt your secrets use the following steps:

  1. Create or use an existing KMS Key - http://docs.aws.amazon.com/kms/latest/developerguide/create-keys.html

  2. Click the "Enable Encryption Helpers" checkbox

  3. Paste <COMMAND_TOKEN> into the kmsEncryptedToken environment variable and click encrypt


Follow these steps to complete the configuration of your command API endpoint

  1. When completing the blueprint configuration select "Open" for security
     on the "Configure triggers" page.

  2. Enter a name for your execution role in the "Role name" field.
     Your function's execution role needs kms:Decrypt permissions. We have
     pre-selected the "KMS decryption permissions" policy template that will
     automatically add these permissions.

  3. Update the URL for your Slack slash command with the invocation URL for the
     created API resource in the prod stage.
"""

import boto3
import json
import logging
import os

from base64 import b64decode
import urllib
from urllib import request
from urllib.parse import parse_qs


ENCRYPTED_EXPECTED_SLASH_TOKEN = os.environ['kmsEncryptedSlashToken']
ENCRYPTED_EXPECTED_APP_TOKEN = os.environ['kmsEncryptedAppToken']
ENCRYPTED_BOT_ACCESS_TOKEN = os.environ['kmsEncryptedBotUserOAuthAccessToken']

kms = boto3.client('kms')
expected_slash_token = kms.decrypt(CiphertextBlob=b64decode(ENCRYPTED_EXPECTED_SLASH_TOKEN))['Plaintext'].decode()
expected_app_token = kms.decrypt(CiphertextBlob=b64decode(ENCRYPTED_EXPECTED_APP_TOKEN))['Plaintext'].decode()
bot_access_token = kms.decrypt(CiphertextBlob=b64decode(ENCRYPTED_BOT_ACCESS_TOKEN))['Plaintext'].decode()

expected_tokens = (expected_slash_token, expected_app_token)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else res,
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    params = parse_qs(urllib.parse.unquote(b64decode(event['body'].encode()).decode()))
    logger.info(params)

    if 'payload' in params:
        payload = json.loads(params['payload'][0])
        trigger_id = payload.get('trigger_id')
        if trigger_id:
            logger.info(trigger_id)
            data = json.dumps({
              "trigger_id": f"{trigger_id}",
              "view": {
                "type": "modal",
                "callback_id": "modal-identifier",
                "title": {
                  "type": "plain_text",
                  "text": "Just a modal"
                },
                "blocks": [
                  {
                    "type": "section",
                    "block_id": "section-identifier",
                    "text": {
                      "type": "mrkdwn",
                      "text": "*Welcome* to ~my~ Block Kit _modal_!"
                    },
                    "accessory": {
                      "type": "button",
                      "text": {
                        "type": "plain_text",
                        "text": "Just a button"
                      },
                      "action_id": "button-identifier"
                    }
                  }
                ]
              }
            }).encode()
            req =  request.Request('https://slack.com/api/views.open', data=data, headers={
                'Content-Type': 'application/json', 'Authorization': f'Bearer {bot_access_token}'})
            resp = request.urlopen(req)
            logging.info(resp.read().decode('utf8'))
            return respond(None)

    token = params['token'][0]
    if token not in expected_tokens:
        logger.info(expected_tokens)
        logger.error('Request token (%s) does not match expected', token)
        return respond(Exception('Invalid request token'))

    user = params['user_name'][0]
    command = params['command'][0]
    channel = params['channel_name'][0]
    if 'text' in params:
        command_text = params['text'][0]
    else:
        command_text = ''

    return respond(None, """{
      "type": "modal",
      "callback_id": "modal-identifier",
      "title": {
        "type": "plain_text",
        "text": "Just a modal"
      },
      "blocks": [
        {
          "type": "section",
          "block_id": "section-identifier",
          "text": {
            "type": "mrkdwn",
            "text": "*Welcome* to ~my~ Block Kit _modal_!"
          },
          "accessory": {
            "type": "button",
            "text": {
              "type": "plain_text",
              "text": "Just a button",
            },
            "action_id": "button-identifier",
          }
        }
      ],
    }""")
