import cgi
import os
import datetime
import wsgiref.handlers
import pickle

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

#Load the database into memory
#TODO: Use a proper database solution
f = open("db.pickle")
db = pickle.load(f)
f.close()

#Class for displaying executed prisoner data based on URL data
class Executed(webapp.RequestHandler):
    def get(self):
        request = self.request.get("name")

        if request in db.keys():
            path = os.path.join(os.path.dirname(__file__), 'executed.html')
            self.response.out.write(template.render(path, db[request]))
        else:
            self.redirect("/")

#Class for displaying main page
class MainPage(webapp.RequestHandler):
    def get(self):
        li = self.createDatabase()

        args = {
            "names":li
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, args))

    def createDatabase(self):
        """Django does not like python dicts. Here is a dirty hack around it
        Rather then attempt to parse this in Django templates we create an array
        filled with preformatted data and pass that to the template"""
        #TODO: FIX THIS HACK OR FIND WORKAROUND
        ret = []
        for i in db:
            if ('ident' in db[i]) and ('name' in db[i]):
                name = db[i]['name']
                ident = db[i]['ident']
                ret.append("<li><a href=/executed?name=" + ident + ">" + name + "</a></li>")

        return ret


#Page handlers
application = webapp.WSGIApplication([
  ('/',         MainPage),
  ('/executed', Executed)
], debug=True)


def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
