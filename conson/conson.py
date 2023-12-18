import os
import json
from cryptography.fernet import Fernet
import subprocess
import hashlib

green = "\033[92m"
red = "\033[91m"
reset = "\033[0m"


class Conson:
    """
    Simple configuration file manager. Create parameters, save them to file in json format, load them back.
    Methods: "create", "create_pwd", "unveil", "save", "load".
    Default parameters: "self.file" - absolute path to config file,
                        "self.clean_salt" - salt string value.
    """
    def __init__(self, cfile="config.json", cfilepath=os.getcwd(), salt="ch4ng3M3pl3453"):
        """
        You can specify configuration file name and location.
        By default, config file is located in program working directory, named "config.json".
        :param cfile: string, i.e. "name.json"
        :param cfilepath: string, path to config file location (without file name)
        :param salt: string, used for additional encryption hardening.
        """
        self.__fullpath = os.path.join(cfilepath, cfile)
        self.__clean_salt = salt
        self.__salt = bytes.fromhex("".join(hex(ord(char))[2:] for char in self.__clean_salt))

    def __call__(self):
        vardict = self.__dict__.copy()
        del vardict["_Conson__fullpath"]
        del vardict["_Conson__salt"]
        del vardict["_Conson__clean_salt"]
        return vardict

    @property
    def file(self):
        return self.__fullpath

    @file.setter
    def file(self, filename, cfilepath=os.getcwd()):
        self.__fullpath = os.path.join(cfilepath, filename)

    @property
    def salt(self):
        return self.__clean_salt

    @salt.setter
    def salt(self, salt_value):
        self.__clean_salt = salt_value

    def __check(self):
        """
        Checks if config file exists and has JSON-loadable format.
        :return: bool
        """
        try:
            with open(self.__fullpath, "r")as config:
                return isinstance(json.load(config), dict)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return False

    def create(self, **args):
        """
        Creates parameter.
        :param args: key=value -> string, int, bool
        """
        for k, v in args.items():
            setattr(self, k, v)

    def __get_key(self):
        """
        Method used for obtaining system UUID for both nt and unix systems.
        Allows to decrypt data only on system where it was encrypted.
        :return: String
        """
        # Converting salt string into md5 hash
        md5 = hashlib.md5()
        md5.update(self.__salt)
        supersalt = md5.hexdigest()

        if os.name == "nt":     # Windows compatibility.
            key = subprocess.check_output(['wmic', 'csproduct', 'get', 'UUID'], text=True) \
                .strip().splitlines()[2].replace("-", "")
            # Extending 32 to 44 bytes using md5 salt, required by Fernet.
            key = (key[:16] + supersalt[16:32] + supersalt[:2] + supersalt[5:7] + key[7:9] + supersalt[16:18]
                   + key[21:23] + key[29] + "=")
            return key.encode()
        elif os.name != "nt":   # Linux/UNIX compatibility.
            key = subprocess.check_output(['dmidecode', '-s', 'system-uuid'], text=True) \
                .strip().splitlines()[2].replace("-", "")
            # Extending 32 to 44 bytes using md5, required by Fernet.
            key = (key[:16] + supersalt[16:32] + supersalt[:2] + supersalt[5:7] + key[7:9] + supersalt[16:18]
                   + key[21:23] + key[29] + "=")
            return key.encode()

    def veil(self, key, index=0):
        """
        Encrypts created parameter.
        E.g.: for
        <instance>.create(pc1=["login", "password"])
        encrypting "password will be:
        <instance>.veil("pc1", 1)
        :param key: string -> key containing value you want to encrypt
        :param index: int -> value index
        """
        values = self()[key]
        if isinstance(values, list):
            encrypted = Fernet(self.__get_key()).encrypt(values[index].encode()).hex()
            values.pop(index)
            values.insert(index, encrypted)
            setattr(self, key, values)
        else:
            encrypted = Fernet(self.__get_key()).encrypt(values.encode()).hex()
            setattr(self, key, encrypted)

    def unveil(self, encrypted_value):
        """
        Allows to decrypt values encrypted with create_pwd method.
        :param encrypted_value: String containing hexadecimal number.
        :return: String /w decrypted password.
        """
        return Fernet(self.__get_key()).decrypt(bytes.fromhex(encrypted_value)).decode()

    def save(self):
        """
        Saves created parameters to file (default: config.json in working directory)
        :return: string - saving result
        """
        try:
            variables = {}
            with open(self.__fullpath, "w") as config:
                for k, v in self().items():
                    if k != "fullpath":
                        variables[k] = v
                json.dump(variables, config, indent=4)
            print("{}CONFIG SAVE SUCCESS!{}".format(green, reset))
        except Exception as err:
            print("{}CONFIG SAVE ERROR:{} {}".format(red, reset, err))

    def load(self):
        """
        Loads parameters from file and passes them to instance.
        :return: string - loading result
        """
        if self.__check():
            with open(self.__fullpath, "r")as config:
                variables = json.load(config)
                for k, v in variables.items():
                    setattr(self, k, v)
                print("{}CONFIG READ SUCCESS{}".format(green, reset))
        else:
            print("{}CONFIG READ ERROR{}".format(red, reset))
