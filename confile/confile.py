import os
import json
from cryptography.fernet import Fernet
import subprocess

green = "\033[92m"
red = "\033[91m"
reset = "\033[0m"


class Confile:
    """
    Simple configuration file manager. Create parameters, save them to file in json format, load them back.
    Methods: "create", "create_pwd", "unveil", "save", "load".
    Default parameters: "self.file" - absolute path to config file.
    """
    def __init__(self, cfile="config.json", cfilepath=os.getcwd()):
        """
        You can specify configuration file name and location.
        By default, config file is located in program working directory, named "config.json".
        :param cfile: string, i.e. "name.json"
        :param cfilepath: string, path to config file location (without file name)
        """
        self.fullpath = os.path.join(cfilepath, cfile)

    def __call__(self):
        vardict = self.__dict__.copy()
        del vardict["fullpath"]
        return vardict

    @property
    def file(self):
        return self.fullpath

    @file.setter
    def file(self, filename, cfilepath=os.getcwd()):
        self.fullpath = os.path.join(cfilepath, filename)

    def __check(self):
        """
        Checks if config file exists and has JSON-loadable format.
        :return: bool
        """
        try:
            with open(self.fullpath, "r")as config:
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

    @staticmethod
    def __get_key():
        """
        Method used for obtaining system UUID for both nt and unix systems.
        Allows to decrypt data only on system where it was encrypted.
        :return: String
        """
        if os.name == "nt":     # Windows compatibility.
            key = subprocess.check_output(['wmic', 'csproduct', 'get', 'UUID'], text=True) \
                .strip().splitlines()[2].replace("-", "")
            key = (key + key[:11] + "=")    # Extending 32 to 44 bytes, required by Fernet.
            return key.encode()
        elif os.name != "nt":   # Linux/UNIX compatibility.
            key = subprocess.check_output(['dmidecode', '-s', 'system-uuid'], text=True) \
                .strip().splitlines()[2].replace("-", "")
            key = (key + key[:11] + "=")    # Extending 32 to 44 bytes, required by Fernet.
            return key.encode()

    @staticmethod
    def unveil(v):
        """
        Allows to decrypt values encrypted with create_pwd method.
        :param v: String containing hexadecimal number.
        :return: String /w decrypted password.
        """
        return Fernet(Confile.__get_key()).decrypt(bytes.fromhex(v)).decode()

    def create_pwd(self, **args):
        """
        Creates parameter with encrypted value.
        :param args: key=value -> string, int, bool
        """
        for k, v in args.items():
            setattr(self, k, Fernet(Confile.__get_key()).encrypt(v.encode()).hex())

    def save(self):
        """
        Saves created parameters to file (default: config.json in working directory)
        :return: string - save result
        """
        try:
            variables = {}
            with open(self.fullpath, "w") as config:
                for k, v in self().items():
                    if k != "fullpath":
                        variables[k] = v
                json.dump(variables, config, indent=4)
            print("{}CONFIG SAVE SUCCESS!{}".format(green, reset))
        except Exception as err:
            print("{}CONFIG SAVE ERROR:{} {}".format(red, reset, err))

    def load(self):
        """
        Loads parameters from file and passes them to creator.
        :return: string - load result
        """
        if self.__check():
            with open(self.fullpath, "r")as config:
                variables = json.load(config)
                for k, v in variables.items():
                    self.create(k=v)
                print("{}CONFIG READ SUCCESS{}".format(green, reset))
        else:
            print("{}CONFIG READ ERROR{}".format(red, reset))
