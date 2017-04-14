import requests
from getpass import getpass
from HTMLParser import HTMLParser
from SidGetter import SidGetter
from datetime import timedelta, datetime, tzinfo
from Cinserter import *

        
# user = raw_input("Login: ")
# password = getpass("Password: ")

def get_booked_lessons(user, password):
    session = requests.Session()
    mainURL = 'https://myclass.britishcouncil.org/eu/index.php'
    sidgetter = SidGetter()
    sidresp = session.post(mainURL, data={'action': 'login', 'id': user, 'pw': password, 'rememberusername': 0})
    sidgetter.feed(sidresp.text)
    plusreq = '?action=getBookingByStudentId&sid=%s' % (sidgetter.sid)
    res = session.get(mainURL+plusreq)
    session.close()
    return res.json()


def main():
    user = raw_input("British Counsli login: ")
    password = getpass("Password: ")

    lessons = get_booked_lessons(user, password)

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    for lesson in lessons:
        time = datetime.strptime(lesson['lt_time'], '%Y-%m-%d %H:%M:%S')
        if time < datetime.now():
            continue
        event = {
            'summary': "English: " + lesson['lt'],
            'description': "%s - %s with %s %s in classroom %s" % (lesson['lt'], lesson['tn'], lesson['tne'], 
                                                            lesson['tsne'], lesson['lt_clsrm']),
            'start':{
                'dateTime': time.isoformat(),
                'timeZone': 'Europe/Kiev'
            },
            'end':{
                'dateTime': (time+timedelta(hours=2)).isoformat(),
                'timeZone': 'Europe/Kiev'
            },
            'id': lesson['id'],
            'reminders': {
                           'useDefault': False,
                           'overrides': []
                         }
        }
        try:
            if service.events().get(calendarId='primary', eventId=lesson['id']).execute()[u'status'] == u'cancelled':
                raise discovery.HttpError('Oops', "don't cry")
        except discovery.HttpError:
            try:
                service.events().insert(calendarId='primary', body=event).execute()
            except discovery.HttpError:
                service.events().insert(calendarId='primary', body={k:v for k, v in event.items() if k!='id'}).execute()
    

if __name__ == '__main__':
    main()