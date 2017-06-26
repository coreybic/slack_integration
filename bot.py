# -*- coding: utf-8 -*-
"""
Python Slack Bot class for use with the pythOnBoarding app
"""
import os
import message
from pprint import pprint
import requests
from requests.auth import HTTPDigestAuth


from slackclient import SlackClient

# To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
authed_teams = {}


class Bot(object):
    """ Instanciates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "pythonboardingbot"
        self.emoji = ":robot_face:"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = SlackClient('xoxb-199478894433-AGEwioHko8y8cBq3ixyNFCZ0')
        # We'll use this dictionary to store the state of each message object.
        # In a production envrionment you'll likely want to store this more
        # persistantly in  a database.
        self.messages = {}


    def question_get(self, team_id, channel_id, user_id, ts):
        #request for the message at the same time in the same channel by the same user
        #format it and send it to ahub
        switch = False
        slack_data = self.client.api_call(
                                "im.history",
                                channel = channel_id,
                                latest = ts,
                                inclusive = 'true',
                                count = 1
                                )
        slack_message = slack_data['messages'][0]['text']

        headers = {
               'Accept': 'application/json',
               'Content-type': 'application/json'}
        params = {'spaceId': '27' }
        data = {'title':slack_message}

        questions = requests.get("https://nominum.cloud.answerhub.com/services/v2/question.json", 
            auth = ('coreybic', 'nominum76'),
            headers = headers,
            params = params).json()

        for q in questions['list']:
            if q['title'] != slack_message and switch:
                ask = requests.post("https://nominum.cloud.answerhub.com/services/v2/question.json", 
                    auth = ('coreybic', 'nominum76'),
                    headers = headers,
                    params = params,
                    data = data).json()

        title = questions['list'][0]['title']

        pprint(title)

        #do space id



        #pprint(slack_data['messages'][0]['text'])

