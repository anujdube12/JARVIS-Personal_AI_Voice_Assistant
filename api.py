import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
from datetime import timedelta, datetime
from RespondListen import respond, listen
import pytz

SCOPES = ['https://www.googleapis.com/auth/calendar']
IST = pytz.timezone("Asia/Kolkata")

def calendar_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('calendar', 'v3', credentials=creds)
    return service
    
def Get_Min_Max_times(now):
    Min = now
    date = now.date()
    Max = (datetime(date.year, date.month, date.day, 0)+timedelta(days = 2)).astimezone(IST)
    return Min.isoformat(), Max.isoformat()

def calendar():
    service = calendar_service()
    now = datetime.now(IST)
    timeMin, timeMax = Get_Min_Max_times(now)
    print('Getting the upcoming events')
    event_results = service.events().list(calendarId='primary', timeMin=timeMin, 
                                          timeMax=timeMax, maxResults=10, 
                                          singleEvents=True, orderBy='startTime').execute()
    events = event_results.get('items', [])
    if not events:
        respond("No upcoming events found.")
    for event in events:
        start_time = event['start'].get('dateTime')
        date_time = start_time.split("T")
        event_date = date_time[0]
        event_time = date_time[1].split("+")
        respond("{} class is at {} {}".format(event['summary'], event_time[0], event_date))
    return 

def create_event():
    service = calendar_service()
    date = datetime.now().date()
    tomorrow = datetime(date.year, date.month, date.day, 10)+timedelta(days = 1)
    start = tomorrow.isoformat()
    end = (tomorrow + timedelta(hours = 1)).isoformat()
    respond("summary of the event")
    summary = listen()
    event = {
        'summary': summary,
        'start': {
            'dateTime': start,
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end,
            'timeZone': 'Asia/Kolkata',
        },
        'attendees' : [
            {'email' : 'kvn8501979409@gmail.com'}
        ]
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    respond("event created successfully")
    return