Module for creating parameters, saving them and loading from JSON formatted file.

    from .conson import Conson

Usage:

1. Conson(cfile="config.json", cfilepath=os.getcwd(), salt="ch4ng3M3pl3453"):
    You can set file name/extension and path to config file directory. By default, current working directory is used.

2. Instance call, parameters:
   Calling Conson instance will return all kwargs that has already been set by create method.
   Values modified with .veil method will be encrypted and presented in hex value.
   Parameters:

        <instance>.file
        <instance>.file = <filename>, <cfilepath=os.getcwd()>

        <instance>.salt
        <instance>.salt = <your salt>

3. .create(key, *value): 
    Creates parameter in key=value pair. Accepts single value or list of values.
    Example:

        settings = Conson()

        settings.create(key1, value1, value2, value3)
        settings.create(key2, [value1, value2, value3])

4. .dispose(key):
    Removes created parameter from instance.

5. .veil(key, index=0):
    Passes created value through Fernet SHA-256 encryption. We point the key and value index number.
    Secret key is based on system-related UUID, so decryption is meant to happen only on device the encryption has place.
    Example:

       settings.veil("setting1")
       settings.veil("setting3", 1)
   
   Result print(settings()):

       "setting1": "674141414141426c65566a6c6123123330617a41416c6330307a3667794a41535965537733423sdvb347705f464a5648435a39596b586a45304b31506232646b645353355f2d4c4646623546fggf3395a6c4e38595f7358676269513d3d"
       "setting3": "value1", "674141414141426c65566a6c6123123330617a41416c6330307a3667794a41535965537733423sdvb347705f464a5648435a39596b586a45304b31506232646b645353355f2d4c4646623546fggf3395a6c4e38595f7358676269513d3d"

6. .unveil(value):
    Allows to decrypt veiled(encrypted) values. Value must be already present in instance (by .create or .load).
    Example:

       settings.unveil(settings()["setting1"])
       settings.unveil(settings()["setting3"][1])

7. .save():
    Saves all parameters created to file. Prints result of operation (success/failure).

8. .load():
    Loads json formatted settings from file. Prints result of operation (success/failure).



   
