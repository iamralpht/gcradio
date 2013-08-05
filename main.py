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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

class KeywordPreferences(ndb.Model):
    user_id = ndb.StringProperty(indexed=True)
    keywords = ndb.StringProperty(repeated=True)
    keyword_weights = ndb.FloatProperty(repeated=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):

        user, prefs = getUserPreferences()

        if user:
            username = user.nickname()

            login_url = users.create_logout_url(self.request.uri)
            login_url_linktext = 'Logout'


            print "Prefs: %s" % prefs
        else:
            username = "Guest"

            login_url = users.create_login_url(self.request.uri)
            login_url_linktext = 'Login'

        template_values = {
            'username' : username,
            'keywords' : ", ".join(prefs.keywords or []),
            'login_url': login_url,
            'login_url_linktext': login_url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

def getUserPreferences():

    user = users.get_current_user()
    if user:
        # TODO: There should be only one result. Must be a better way
        query = KeywordPreferences.query(KeywordPreferences.user_id == user.user_id())
        try:
            prefs = query.fetch(1)[0]
        except IndexError:
            prefs = KeywordPreferences()
            prefs.user_id = user.user_id()
    else:
        prefs = KeywordPreferences()
    return user, prefs

class EditKeywordsHandler(webapp2.RequestHandler):
    def post(self):

        content = cgi.escape(self.request.get('content'))
        keywords = [x.strip() for x in content.split(",")]

        user, prefs = getUserPreferences()
        prefs.keywords = keywords
        key = prefs.put()
        print key

        self.redirect("/")

class NextHandler(webapp2.RequestHandler):
    def get(self):
        result = {
            "storyId" : "foo",
            "programName" : "NPR Insights",
            "storyName" : "Episode 26: Mild voices",
            "mediaPath" : "http://www.google.com/url?q=http%3A%2F%2Fpd.npr.org%2Fanon.npr-mp3%2Fwbur%2Fmedia%2F2013%2F08%2F20130805_hereandnow_africa-st-louis.mp3&sa=D&sntz=1&usg=AFQjCNEJd6YcPBtXU9AP0XhKO8fquKrkFw",
            "summary" : "A thrilling look into the consistency of NPR anchors and their speaking voices.",
        }
        resultJson = json.dumps(result)
        self.response.write(resultJson)

class ThumbsUpHandler(webapp2.RequestHandler):
    def get(self):
        user, prefs = getUserPreferences()

        storyId = self.request.get('storyId')
        self.response.write(storyId)

class ThumbsDownHandler(webapp2.RequestHandler):
    def get(self):
        user, prefs = getUserPreferences()

        storyId = self.request.get('storyId')
        self.response.write(storyId)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/edit_keywords', EditKeywordsHandler),
    ('/next', NextHandler),
    ('/thumbs-up', ThumbsUpHandler),
    ('/thumbs-down', ThumbsDownHandler),
], debug=True)
