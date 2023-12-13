Module for creating parameters, saving them and loading from JSON formatted file.

    from .confile import Confile

Usage:

1. Confile(cfile="config.json", cfilepath=os.getcwd()):
    You can set file name/extension and path to config file directory. By default, current working directory is used.

2. Instance call:
   Calling Confile instance will return all kwargs that has already been set by create and create_pwd methods.
   Values created with create_pwd method will be encrypted and presented in hex value.
   You can also use print(vars("Confile object))) to return kwargs with absolute path to config file.

3. .create(**kwargs): 
    Creates parameter in key=value pair. Accepts multiple keyword values.
    Example:

        settings = Confile()

        settings.create(setting1="value1", setting2=True, setting3=["value1", "value2"])

4. .veil(**kwargs):
    Same as .create, except value will be processed through Fernet SHA-256 encryption.
    Secret key is based on system-related UUID, so decryption is meant to happen only on device the encryption has place.
    Example:

       settings.veil(password1="topsecret")
   
   Result print(settings()):

       'password1':'674141414141426c65566a6c6123123330617a41416c6330307a3667794a41535965537733423sdvb347705f464a5648435a39596b586a45304b31506232646b645353355f2d4c4646623546fggf3395a6c4e38595f7358676269513d3d'

6. .unveil(value):
    Allows to decrypt veiled(encrypted) values. Value must be present in instance (by .create or .load).
    Example:

       settings.unveil(settings()["password1"])

7. .save():
    Saves all parameters created to file. Prints result of operation (succes/failure).

8. .load():
    Loads json formatted settings from file. Prints result of operation (succes/failure).



   
