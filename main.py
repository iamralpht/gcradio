#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import cgi
from google.appengine.api import users
from google.appengine.ext import ndb
import json
import random

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class UserPreferences(ndb.Model):
    keywords = ndb.StringProperty(repeated=True)
    keyword_weights = ndb.FloatProperty(repeated=True)
    history = ndb.JsonProperty(indexed=False)

class Story(ndb.Model):
    story_id = ndb.StringProperty()
    program_id = ndb.StringProperty()
    audio_url = ndb.StringProperty(indexed=False)
    image_url = ndb.StringProperty(indexed=False)
    story_title = ndb.StringProperty(indexed=False)
    text = ndb.StringProperty(indexed=False)
    program_name = ndb.StringProperty(indexed=False)
    tags = ndb.JsonProperty(indexed=False)

class MainHandler(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        prefs = getUserPreferences(user)

        if user:
            username = user.nickname()

            login_url = users.create_logout_url(self.request.uri)
            login_url_linktext = 'Logout'

            keywords = ", ".join(prefs.keywords or [])

            print "Prefs: %s" % prefs
        else:
            username = "Guest"

            login_url = users.create_login_url(self.request.uri)
            login_url_linktext = 'Login'

            keywords = ""

        template_values = {
            'username' : username,
            'keywords' : keywords,
            'login_url': login_url,
            'login_url_linktext': login_url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

def getUserPreferences(user):
    if user is None:
        return UserPreferences()
    prefs = UserPreferences.get_by_id(user.user_id())
    if prefs is None:
        prefs = UserPreferences(id=user.user_id())
        prefs.keywords = []
        prefs.put()
    return prefs

class EditKeywordsHandler(webapp2.RequestHandler):
    def post(self):

        content = cgi.escape(self.request.get('content'))
        keywords = [x.strip() for x in content.split(",")]

        user = users.get_current_user()
        prefs = getUserPreferences(user)

        prefs.keywords = keywords
        key = prefs.put()
        print key

        self.redirect("/")

class NextHandler(webapp2.RequestHandler):
    def get(self):

        story = self.getRandomStory()
        result = story.to_dict()

        resultJson = json.dumps(result)
        self.response.write(resultJson)

    def getRandomStory(self):
        query = Story.query()
        stories = list(query)
        randomIndex = random.randint(0,len(stories))
        randomStory = stories[randomIndex]
        return randomStory


class ThumbsUpHandler(webapp2.RequestHandler):
    def get(self):

        storyId = self.request.get('storyId')
        result = {"story_id" : storyId, "status" : "thumbs-up"}

        user = users.get_current_user()
        prefs = getUserPreferences(user)

        history = prefs.history or []

        history.append(result)
        prefs.history = history
        prefs.put()

        self.response.write(json.dumps(result));

class ThumbsDownHandler(webapp2.RequestHandler):
    def get(self):

        storyId = self.request.get('storyId')
        result = {"story_id" : storyId, "status" : "thumbs-down"}

        user = users.get_current_user()
        prefs = getUserPreferences(user)

        history = prefs.history or []

        history.append(result)
        prefs.history = history
        prefs.put()

        self.response.write(json.dumps(result));

class InsertTestDataHandler(webapp2.RequestHandler):
    def get(self):

        jsonFile = open('story_data.json')
        jsonStories = json.load(jsonFile)
        jsonFile.close()

        count=0
        for jsonStory in jsonStories:
            program_id = str(jsonStory["program_id"])
            program_name = jsonStory["program_name"]
            story_id = jsonStory["story_id"]
            story_title = jsonStory["story_title"]["$text"]
            audio_url = jsonStory["audio_url"]
            image_url = jsonStory["image_url"]
            text = jsonStory["text"]
            tags = jsonStory["tags"]

            story = Story(id=story_id
                ,program_id=program_id
                ,program_name=program_name
                ,story_id=story_id
                ,story_title=story_title
                ,audio_url=audio_url
                ,image_url=image_url
                ,text=text
                ,tags=tags
            )
            story.put()
            count += 1
            
        self.response.write("Inserted %s records" % count)

class HistoryHandler(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        prefs = getUserPreferences(user)

        history = prefs.history

        self.response.write(history)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/edit_keywords', EditKeywordsHandler),
    ('/next', NextHandler),
    ('/thumbs-up', ThumbsUpHandler),
    ('/thumbs-down', ThumbsDownHandler),
    ('/history', HistoryHandler),
    ('/insert_test_data', InsertTestDataHandler),
], debug=True)
