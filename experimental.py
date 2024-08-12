import os
import mfrc522 as MFRC522 
from collections.abc import Iterable
import json
import configparser
import threading
import time
import google.auth 
import RPi.GPIO as GPIO 
from googleapiclient.discovery import build 
from googleapiclient.errors import HttpError 
from google.auth.transport.requests import Request 
from google.oauth2.credentials import Credentials 
from google_auth_oauthlib.flow import InstalledAppFlow 


target_sector = 2

config_object = configparser.ConfigParser()

# Section for opening and reading the ini file into a single object
with open("Data/machine.ini", "r") as file_object:
    config_object.read_file(file_object)


# Allowing for future access to other blocks using the same function by checking against the following constants
CONSTANT_MEMBER_ID_BLOCK = 10
CONSTANT_ADD_DATA_BLOCK = 9


# These are the user defined scopes, you can change this based on what the scanner needs to write/read to/from and you can add or remove scopes as listed in the google api
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"] 

# This is the number of the machine, please configure this based off of what the service-end code requires
linkedMachine = int(config_object.get("MachineInfo", "MACHINEID")) 

MIFAREReader = MFRC522.MFRC522() # If you are using the rc522 scanner keep this and all associated calls in the code, otherwise you'll lose certain functionality 

# Status Identifiers
currentUser = None
currentStatus = "Inactive"


sId = "1zy07fuvIi8Zjh64PXCPjqMoRseUnffRyuTZYEWfh00Y" # The google sheet that is being written to by the software, in this case it is a test spreadsheet that will be changed later on 


# Gets values from the google sheet that we defined in the sId field
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

def read_data():
    f = open('Data/StatusData.json')
    data = json.load(f)
    f.close()
    return data['user'],data['status']

def write_data(person, status):
    with open('Data/StatusData.json', 'r+') as f:
        data = json.load(f)
        data['user'] = person # <--- add `id` value.
        data['status'] = status
        f.seek(0)        # <--- should reset file position to the beginning.
        json.dump(data, f, indent=4)
        f.truncate()     # remove remaining part
        f.close()


# Communication with the status panel db online, it comms with google (might make it run on a seperate thread for more efficiency)
def status_updater(cardNum, tMaId):
    maIdc = get_values(
        sId,
        "MACHINEIDS"
    )
    cuserc = get_values(
        sId,
        "CURRENTUSERS"
    )
    ms_column = get_values(
        sId,
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


def read_card():
    target = ""
    ic, ver, rev, support = pn532.get_firmware_version()
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

    # Configure PN532 to communicate with MiFare cards
    pn532.SAM_configuration()

    print('Waiting for RFID/NFC card to read from!')
    while True:
        # Check if a card is available to read
        uid = pn532.read_passive_target(timeout=0.5)
        print('.', end="")
        # Try again if no card is available.
        if uid is not None:
            break
    print("Card Found, Reading number...")
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    # Now we try to go through all 16 sectors (each having 4 blocks)
    try:
        pn532.mifare_classic_authenticate_block(uid, block_number=target_sector,key_number=nfc.MIFARE_CMD_AUTH_A, key=key_a)
        print("Block Number 2:",':', ''.join(['%s' % x for x in pn532.mifare_classic_read_block(target_sector)]))
        for i in pn532.mifare_classic_read_block(target_sector):
            if(i != 0):
                target = target + chr(i)
    except nfc.PN532Error as e:
        print(e.errmsg)
    int(target)
    return target


# The central function that allows for reading from the RFID reader and then using that data to input to the google sheets
def read_data_from_block(block_num):
    (currentUser, currentStatus) = read_data()
    text_read = ''
    # Scan For Cards
    (status, uid) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    # If a card is found
    if status == MIFAREReader.MI_OK:
        print()

    (status, uid) = MIFAREReader.MFRC522_Anticoll()
    
    if status == MIFAREReader.MI_OK:
        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF] # Default auth key, remains unchanged for most systems
        MIFAREReader.MFRC522_SelectTag(uid) # 
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 2, key, uid)
        if status == MIFAREReader.MI_OK:
            print("Printed Read Data:")
            data = MIFAREReader.MFRC522_Read(2)
            print(data)
            # This function checks if the returned data is iterable
            if isinstance(data, Iterable):
                # Prints out to the console that the data is iterable and proceeds with constructing the string
                print("Iterable data acquired...")
                text_read = ""
                
                # Handles construction of the string ommiting any zeros and preventing the addition of a NULL escape code
                for i in data:
                    if i == 0:
                        print("Nah.")
                    else:
                        print("Character Read: {0}".format(chr(i)))
                        text_read = text_read + str(chr(i))
                if text_read[0] == '0':
                    text_read = text_read[1:]
                

                status_updater(text_read, linkedMachine)
                # status_updater(text_read, linkedMachine) This was formerly used to update the status on the google sheets using the google api, now we dont use it here
                print("Here is the read data: %s" % text_read)
                MIFAREReader.MFRC522_StopCrypto1()
            else:
                # Just an error message returned by the program if the card reader fails to read a card, fairly unlikely thanks to the way we'll go about implementing it 
                print("Error in reading")
                text_read = ""
                MIFAREReader.MFRC522_StopCrypto1()
        else:
            print("Auth error!!!!!!")
    return text_read



goalBlock = 10


# The main method of the program, and acts as the main area where code is executed and sequenced from
if __name__ == "__main__":
    while True:
        (cUser, cStat) = read_data() # Used first to check if someones using the machine, and then uses that information to then produce a light set
        # Here is where lighting will go
        # Add lighting for the cool gamer color...
        badge = read_card()
        # Here is how this pos determines the person inside ;)
        if cUser == str(badge):
            write_data("None", "Inactive") # If the same person taps, the machine goes idle
        else:
            write_data(str(badge), "Active") # Otherwise, kick that person out and start a new session    
        status_updater(badge, linkedMachine) # Does the same as the above, but reflects the changes to the google sheet lol ()
        


