import httplib2
import datetime
import os
import re

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Port City Makerspace Door Locks'
#Replace this ID with the real one in production
spreadsheetId = '1FZ2NEDRY8neUYKgq5Bz0FU6DaY-kPkQTvtAFeKiONdI'

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
    credential_path = os.path.join(credential_dir,'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    #Generates dates for expiration compareson
    today = datetime.datetime.combine(datetime.date.today(),datetime.datetime.min.time())
    oneWeek = datetime.timedelta(weeks=1)
    #Google sheets API stuff
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    #These are the ranges with the data we need
    rangeNames = ['Sheet1!A2:E','Sheet1!F2:F','Sheet1!K2:K']
    result = service.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheetId, ranges=rangeNames, valueRenderOption='UNFORMATTED_VALUE', dateTimeRenderOption='SERIAL_NUMBER').execute()
    members = []

    #The data is split across a few chuncks, this gets it all together
    for linenum,line in enumerate(result.get('valueRanges')[0]['values']):
        excelDate = result.get('valueRanges')[1]['values'][linenum][0]
        line.append(datetime.datetime.fromtimestamp((excelDate - 25569) * 86400))
        line.append(result.get('valueRanges')[2]['values'][linenum][0])
        members.append(line)
    
    #Removes the existing data. It trys it becouse if the file doesn't exist,
    #then python complains and stops execution
    try:
        os.remove("MemberCards.txt")
    except OSError as e:
        pass
    
    #Check for blank cells, becouse if there is, it will misalign the whole thing,
    #potentially causing unintended entry
    for member in members:
        if len(member) != 6:
            print("FATAL ERROR: Check the spreadsheet for blank cells")
            os.exit()

    for member in members:
        if member[0] != "#A":
            #print("not active")
            continue
        if member[3] != "Maker's Guild":
            #print("not maker guild")
            continue
        if member[4] < today+oneWeek:
            #print("expired")
            continue
        if re.match("#",member[5]):
            continue
        print("all good")
        with open("MemberCards.txt", "a") as memberCards:
            memberCards.write(member[1] + ' ' + member[2] + ',' + member[5])

def updateCard(cardID,excelLineNo):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

if __name__ == '__main__':
    main()
