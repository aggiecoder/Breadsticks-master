from __future__ import print_function #print function for python
from flask import Flask, render_template, jsonify, request #import flask and also template render for html
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
from datetime import timedelta #*only using this for testing on shell, remove afterwards
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

#create an instance
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('template.html')




# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
#SCOPES = 'https://www.googleapis.com/auth/calendar.readonly' #needed for read only
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Breadsticks Calendar API'

#boiler plate
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

#delete_event(event.get('id'), service)
#same as others so doesnt have html implementation
@app.route('/delete_event', methods=['POST'])
def delete_event():
    service = get_service()
    eventId = request.form['eventId']
    service.events().delete(calendarId='primary', eventId=eventId).execute()
    return jsonify({'success' : 'Deleted Event'})

#arguments need to be passed and initialize data, test data placed here, pass in a json or whatever array you want, we can parse it
@app.route('/create_event', methods=['POST'])
def create_event():
    service = get_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time utc is yyy--mm--dd--ss:hh:mm
    summary = request.form["summary"] #change to what you are using to pass value
    begin_time = now
    end_time = (datetime.datetime.utcnow() + timedelta(hours = 9)).isoformat()
    event = {
      'summary': summary,
      #'location': '800 Howard St., San Francisco, CA 94103',
      #'description': 'A chance to hear more about Google\'s developer products.',
      'start': {
        'dateTime': begin_time,
        #'timeZone': 'America/Chicago',
      },
      'end': {
        'dateTime': end_time,
        'timeZone': 'America/Chicago',
      },
    }
    #*add more metadata as needed
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(event.get('id')) #*Important when editing, or deleting a new event
    return render_template('template.html')
    #here we need a date time type to use, but for now ill just set it myself
    #see if you can just print to input here


#get all events so as to display, everything in the past 24 hours and future
@app.route('/getall/', methods=['POST', 'GET'])
def get_all_events():
    service = get_service()
    now = (datetime.datetime.now() - timedelta(hours = 24)).isoformat() + 'Z' #Last 24 hours and future events
    page_token = None
    while True:
        events = service.events().list(calendarId='primary', timeMin = now, pageToken=page_token ).execute()
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    return jsonify(events)
#event Id is needed to make this work
#get event data to propogate whats needed, returns json. Look on google how to parse data needed
@app.route('/get_event', methods=['POST'])
def get_event():
    service = get_service()
    eventId = request.form['eventId']
    if eventId:
        event = service.events().get(calendarId='primary', eventId=eventId).execute()
        return jsonify(event)
    return jsonify({'error' : 'Missing data!'})


#pass in a json and we will seperate according to
@app.route('/edit_event', methods=['POST'])
def edit_event():
    service = get_service()
    eventId = request.form['eventId']
    event = service.events().get(calendarId='primary', eventId=eventId).execute()
    event['summary'] = request.form['summary']
    #event['start'] = #make sure its in correct format
    #event['end'] = #make sure its in correct format
    updated_event =service.events().update(calendarId='primary', eventId=eventId, body=event).execute()
    return jsonify(updated_event)

@app.route('/login/')
def get_service():
    """Shows basic usage of the Google Calendar API.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http) #service endpoint with http request
    return service
    #create_event(service)
    #delete_event('HERE WE NEED AN EVENT STRING', service)
    #get_all_events(service)
    #get_event('amhqurav21p4rk2u8tfab54ftg', service)
    #edit_event('amhqurav21p4rk2u8tfab54ftg', service)


if __name__ == '__main__':
    #main()
    app.run(debug=True) #changes, remove debug when donev

        # javascript for json, ignore
        # $("#create-button").click(function(){
        #   var formData = JSON.stringify($("#create").serializeArray());
        #   $.ajax({
        #     type: "POST",
        #     url: "/create_event",
        #     datatype:"json",
        #     success: function(){
        #     },
        #     error: function(request, status, error){
        #       console.log("Error:" + error);
        #     }
        #   });
        # });
