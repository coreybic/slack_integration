# -*- coding: utf-8 -*-
"""
Python Slack Bot class for use with the pythOnBoarding app
"""
import os
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
        self.oauth = {"client_id": '3520360656.197273678886',
                      "client_secret": '2aaf0b40f34854835d2ed29c332abc32',
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = 'n3TXdVuM1hM5nBqHBsydmCT5'

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = SlackClient(os.environ.get("client_token"))
        # We'll use this dictionary to store the state of each message object.
        # In a production envrionment you'll likely want to store this more
        # persistantly in  a database.
        self.messages = {}
        self.last_question = -1
        self.last_channel = ''


    def question_get(self, team_id, channel_id, user_id, ts):
        #safeguard for duplicate question posting
        switch = True

        #request for the message at the same time in the same channel by the same user
        #format it and send it to ahub
        slack_data1 = self.client.api_call(
                                "channels.history",
                                channel = channel_id,
                                latest = ts,
                                inclusive = 'false',
                                count = 1
                                )
        slack_data2 = self.client.api_call(
                                "im.history",
                                channel = channel_id,
                                latest = ts,
                                inclusive = 'false',
                                count = 1
                                )

        #pprint(slack_data1)
        pprint(slack_data2['messages'][0]['text'])

        slack_message = ''
        if 'messages' in slack_data1:
            slack_message = slack_data1['messages'][0]['text']
        elif 'messages' in slack_data2:
            slack_message = slack_data2['messages'][0]['text']


        #slack_message = slack_data['messages'][0]['text']
        self.last_channel = channel_id
        pprint(slack_message)

        # headers, paramaters and data to post as question on AHUB
        headers = {
               'Accept': 'application/json',
               'Content-type': 'application/json'}
        params = {'spaceId': 31}

        data = {'title': slack_message,
                'body': slack_message,
                'topics': "slack"}



        # making sure the exact question does not already exist
        questions = requests.get("https://nominum.cloud.answerhub.com/services/v2/question.json", 
            auth = ('slack_bot', 'nominum76'),
            headers = headers,
            params = params).json()

        for q in questions['list']:
            if q['title'] == slack_message:
                switch = False


        #if it is a new question, post it 
        
        if switch:

            host = "https://nominum.cloud.answerhub.com"
            url = host + "/services/v2/question.json"   
            ###########
            #response = requests.post(url, headers=headers, auth=("slack_bot", "nominum76"), params=params, json=data)
            #get question id of posted question for possible answering
            question_id = requests.get("https://nominum.cloud.answerhub.com/services/v2/question.json", 
                auth = ('slack_bot', 'nominum76'),
                headers = headers,
                params = params).json()

            if len(question_id['list']) > 0:
                self.last_question = question_id['list'][0]['id']
                #print last_question
                #pprint(response)
        else:
            print "no"
            
        
        
        #get question id of posted question for possible answering
        """ question_id = requests.get("https://nominum.cloud.answerhub.com/services/v2/question.json", 
            auth = ('slack_bot', 'nominum76'),
            headers = headers,
            params = params).json()

        self.last_question = question_id['list'][0]['id']"""
        #last_question = questions['list'][0]['title']
        #pprint(slack_data['messages'][0]['text'])








    def answer_get(self, team_id, channel_id, user_id, ts):
        switch = True
        slack_data1 = self.client.api_call(
                                "channels.history",
                                channel = channel_id,
                                latest = ts,
                                inclusive = 'false',
                                count = 1
                                )
        slack_data2 = self.client.api_call(
                                "im.history",
                                channel = channel_id,
                                latest = ts,
                                inclusive = 'false',
                                count = 1
                                )


        slack_message = ''
        if 'messages' in slack_data1:
            slack_message = slack_data1['messages'][0]['text']
        elif 'messages' in slack_data2:
            slack_message = slack_data2['messages'][0]['text']


        slack_answer = slack_message
        pprint(slack_message)

        headers = {
               'Accept': 'application/json',
               'Content-type': 'application/json'}
        params = {'spaceId': '31'}


        answers = requests.get("https://nominum.cloud.answerhub.com/services/v2/question/%s/answer.json" % (self.last_question), 
            headers = headers,
            auth = ('slack_bot', 'nominum76'),
            params = params).json()

        for a in answers['list']:
            if a['body'][:15] == slack_answer[:15]:
                switch = False

        if switch and self.last_question != -1 and channel_id == self.last_channel:
            print "yes"
            host = "https://nominum.cloud.answerhub.com"
            url = host + "/services/v2/question/%s/answer.json" % (self.last_question)  
            ##########
            #response = requests.post(url, headers=headers, auth=("slack_bot", "nominum76"), params=params, json={'body': slack_answer})

        else:
            print "no"




