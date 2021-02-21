import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(name)
slack_events_adapter = SlackEventAdapter(os.environ['SigningSecret'],'/slack/events', app)

client = slack.WebClient(token=os.environ['slackToken'])
bot_id = client.api_call("auth.test")["user_id"]


@slack_events_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if bot_id != user_id:
        client.chat_postMessage(channel = channel_id, text= text)


if name == "main":
    app.run(debug=True)