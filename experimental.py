import os
import mfrc522 as MFRC522 
from collections.abc import Iterable
import threading
import time
import google.auth 
import RPi.GPIO as GPIO 
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError 
from google.auth.transport.requests import Request 
from google.oauth2.credentials import Credentials 
from google_auth_oauthlib.flow import InstalledAppFlow 


# Allowing for future access to other blocks using the same function by checking against the following constants
CONSTANT_MEMBER_ID_BLOCK = 10
CONSTANT_ADD_DATA_BLOCK = 9


# These are the user defined scopes, you can change this based on what the scanner needs to write/read to/from and you can add or remove scopes as listed in the google api
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"] 
linkedMachine = 3 # This is the number of the machine, please configure this based off of what the service-end code requires
MIFAREReader = MFRC522.MFRC522() # If you are using the rc522 scanner keep this and all associated calls in the code, otherwise you'll lose certain functionality 

# Status Identifiers
currentUser = None
currentStatus = "Inactive"


sId = "1zy07fuvIi8Zjh64PXCPjqMoRseUnffRyuTZYEWfh00Y" # The google sheet that is being written to by the software, in this case it is a test spreadsheet that will be changed later on 


def update_values(spreadsheet_id, range_name, value_input_option, vs):
   
    # This section here will essentially just be the portion where google verifies access to the api using the OAuth2 system. Nothing really needs to be changed here just focus on creating the proper credentials.json from the google api
    # VERIFICATION SECTION -- Start--
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())
    # VERIFICATION SECTION -- End --
    # The code below will attempt to connect to the google service and write to a specific sheet range that gets plugged into the function's arguments
   # pylint: disable=maybe-no-member
    try:
        service = build("sheets", "v4", credentials=creds)
        values = [
            [
                # Cell values ...
            ],
            # Additional rows ...
        ]
        body = {"values": vs}
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error



# The comments in the previous update_values() function will essentially carry over to this function with little change aside from different parameters defined for the function 
def get_values(spreadsheet_id, range_name):
    creds = None   
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())


    # pylint: disable=maybe-no-member
    try:
        service = build("sheets", "v4", credentials=creds)
        
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        rows = result.get("values", [])
        print(f"{len(rows)} rows retrieved")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


# Will likely be deprecated in favor of new mechanism for holding cards while machine in use
def status_updater(cardNum, tMaId):
    maIdc = get_values(
        "1zy07fuvIi8Zjh64PXCPjqMoRseUnffRyuTZYEWfh00Y",
        "MACHINEIDS"
    )
    cuserc = get_values(
        "1zy07fuvIi8Zjh64PXCPjqMoRseUnffRyuTZYEWfh00Y",
        "CURRENTUSERS"
    )
    ms_column = get_values(
        "1zy07fuvIi8Zjh64PXCPjqMoRseUnffRyuTZYEWfh00Y",
        "MSTATUSES"
    )
    targ = -1
    for i in range(len(maIdc['values'])):
        if str(tMaId) == str(maIdc['values'][i][0]):
            targ = i
    
    mstatusest = "MachineDB!D" + str(targ + 2)
    cuserst = "MachineDB!E" + str(targ + 2)
    

    if str(cuserc['values'][targ][0]) == str(cardNum) and str(ms_column['values'][targ][0]) == "Active":
        print("Turning Off")
        update_values(sId, mstatusest, "USER_ENTERED", [["Inactive"]])
        update_values(sId, cuserst, "USER_ENTERED", [["Vacant"]])
    elif cuserc['values'][targ][0] != str(cardNum) and str(ms_column['values'][targ][0]) == "Active":
        print("Changing User")
        print(str(cuserc['values'][targ][0]))
        update_values(sId, cuserst, "USER_ENTERED",[[cardNum]])
    else:
        print("Ur mom")
        update_values(sId, mstatusest, "USER_ENTERED", [["Active"]])
        update_values(sId, cuserst, "USER_ENTERED", [[cardNum]])
    return "Done."


def open_session(cardNum):
    currentUser = cardNum
    googThread = threading.Thread(target=status_updater, args=(1,))
    
    return

def close_session(cardNum):
    

    return


def read_data_from_block(block_num):
    text_read = ''
    # Scan For Cards
    (status, uid) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    # If a card is found
    if status == MIFAREReader.MI_OK:
        print()

    (status, uid) = MIFAREReader.MFRC522_Anticoll()
    
    if status == MIFAREReader.MI_OK:
        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        MIFAREReader.MFRC522_SelectTag(uid)
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 2, key, uid)
        if status == MIFAREReader.MI_OK:
            print("Printed Read Data:")
            data = MIFAREReader.MFRC522_Read(2)
            print(data)
            if isinstance(data, Iterable):
                print("Iterable data acquired...")
                text_read = ""
                for i in data:
                    if i == 0:
                        print("Nah.")
                    else:
                        print("Character Read: {0}".format(chr(i)))
                        text_read = text_read + str(chr(i))
                if text_read[0] == '0':
                    text_read = text_read[1:]
                
                open_session(text_read)
                status_updater(text_read, linkedMachine)
                print("Here is the read data: %s" % text_read)
                MIFAREReader.MFRC522_StopCrypto1()
            else:
                print("Error in reading")
                text_read = ""
                MIFAREReader.MFRC522_StopCrypto1()
        else:
            print("Auth error!!!!!!")
    elif(status != MIFAREReader.MI_OK and currentUser != None):
        close_session(currentUser)
    return text_read



goalBlock = 10


if __name__ == "__main__":
    print(read_data_from_block(10))

