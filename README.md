
# Check In Machines/Satellites

This repo acts as the host for the python file that runs the check in system for the individual machines, the other check in system is not yet hosted on github 
## Executing

Once The project is installed and configured on a raspberry pi that has the rc522 card reader run the following command:

```bash
  sudo python3 quickstart.py 
```
Running the command listed above will continuously read from the rc522 and then upload any read card information to the database of choice

**Note: When Using a custom database, it is imperative that you modify the python file in the repo to fit your database's requirements and proper access convention**


## General Information

This repo is currently home to the files used to operate the sattelites in the NYC FIRST Stem center on roosevelt island, with the eventual goal being to move across all the stem centers and then putting a single module at each machine that should require some kind of safety or information training

However, all of the code is free for personal or industrial use as noted by the MIT Open-Source License found as License.txt, but please understand that the intended use case for this specific piece of software is to control what individuals are permitted to use or operate specifically defined machines and **should** be modified if for personal and or industrial use.

## Modification instructions

This software contains links and directives that point to a private google spreadsheet id, as a result it wont have the intended impact when used by another individual or user that wont have access to the database as a result please edit the ``` sId ``` Variable prior to any execution otherwise, you wont get the intended impact

```python
    sId = 'YOUR SPREADSHEET ID HERE' # Line 30 in quickstart.py
```

# GScripts

The js file found in the GScripts folder, is not intended for use as a javascript file for a webpage, but is meant for use on the google appscript page, so if you wish to use the functionality, please create a google appscript progject and paste the code while modifying the appropriate fields
