import urllib2
import json


def subject_details(cod):

    subject = None

    try:
        page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/asignaturas/%s/'%(cod)).read()
        subject = json.loads(page)
        if len(subject) > 0:
            subject = subject[0]
    except urllib2.URLError as e:
        pass

    return subject
