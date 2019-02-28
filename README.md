# Drone Configuration Tool
Find feasible drone configurations based on combinations of EDFs, ESCs and battery packs.

To read data from a Google Spreadsheet create a `credentials.json` file as described [here](https://developers.google.com/sheets/api/quickstart/python) and create a file `spreadsheet_id` that only contains the id of the spreadsheet.

Then run the server with `python server.py --loader spreadsheet`.
