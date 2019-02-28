import os
import os.path
import pickle

import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class DataLoader:
    def load_dfs(self):
        raise NotImplementedError

    def load(self):
        dfs = self.load_dfs()
        return [list(df.itertuples()) for df in dfs]


class CsvLoader(DataLoader):
    def __init__(self, path):
        self.path = path
        self.filenames = ['edf.csv', 'esc.csv', 'battery.csv']

    def load_dfs(self):
        paths = (os.path.join(self.path, f) for f in self.filenames)
        dfs = (pd.read_csv(path, thousands=',') for path in paths)
        return  dfs


class SpreadsheetLoader(DataLoader):

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    SPREADSHEET_ID = '1ifkWLrMZiCqrM0Jz0hgi4FTc7MfTREkx-mk4uzgsz7c'

    def build_service(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SpreadsheetLoader.SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)
        return service

    def load_spreadsheet(self, name):
        service = self.build_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SpreadsheetLoader.SPREADSHEET_ID,
                                    range=name).execute()
        values = result.get('values', [])
        columns = values[0]
        data = []
        for row in values[1:]:
            new_row = [row[0]]
            for cell in row[1:]:
                new_row.append(float(cell.replace(',', '')))
            data.append(new_row)
        df = pd.DataFrame(data, columns=columns)
        return df

    def load_dfs(self):
        sheets = ['EDF', 'ESC', 'Battery']
        return [self.load_spreadsheet(sheet) for sheet in sheets]
