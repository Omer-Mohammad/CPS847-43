# env
import os
from pathlib import Path
from dotenv import load_dotenv

# slack
import slack
from slackeventsapi import SlackEventAdapter
from flask import Flask

# API calls
import requests
import enchant

dic = enchant.Dict('en_US')
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SigningSecret'], '/slack/events', app)
client = slack.WebClient(token=os.environ['slackToken'])
bot_id = client.api_call("auth.test")["user_id"]


# on message
@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    text_block = text.split()
    if text_block[0] == 'weather':  # if looking for weather
        weather_message = weather_call(text_block[1:])
        client.chat_postMessage(channel=channel_id, text=weather_message)
    else:
        if bot_id != user_id:
            client.chat_postMessage(channel=channel_id, text=text)


# weather api
def weather_call(input_city):
    city_name = ' '.join(input_city).title() # parse multi word city into one word
    weather_url = \
        'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric'.format(
            city_name=city_name,
            api_key=os.environ['weatherKey'])

    response_string = requests.get(weather_url)

    if response_string.status_code != requests.codes.ok:
        if response_string.status_code == 404:  # one attempt at correction if 404
            word_list = dic.suggest(city_name)  # obtain list of similar words
            new_city = ''
            for word in word_list:  # look for proper noun in similar words
                if word.istitle():
                    new_city = word
                    break

            weather_url = \
                'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric'.format(
                    city_name=new_city,
                    api_key=os.environ['weatherKey'])

            response_string = requests.get(weather_url)
        else:
            return "Error getting weather: " + str(response_string.status_code)

    # if spelling correction still did not work
    if response_string.status_code != requests.codes.ok:
        return "Error getting weather, could not parse city: " + str(response_string.status_code)

    try:
        response_dict = response_string.json()
    except ValueError:
        return "Error getting weather: " + str(response_string.content)

    city = response_dict['name']
    temp = response_dict['main']['temp']
    feels_like = response_dict['main']['feels_like']
    desc = response_dict['weather'][0]['description']

    return_string = 'The weather in {city} is currently {temp}°C and feels like {feels_temp}°C with {desc}.'.format(
        city=city,
        temp=temp,
        feels_temp=feels_like,
        desc=desc
    )

    return return_string


if __name__ == "__main__":
    app.run(debug=True)
