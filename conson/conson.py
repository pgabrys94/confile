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
        self.__salt = bytes.fromhex("".join(hex(ord(char))[2:] for char in self.__clean_salt))

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

    def create(self, k, *v):
        """
        Creates parameter.
        :param k: key name -> string
        :param v: values -> string, list
        """
        if len(list(v)) > 1:
            values = []
            for val in v:
                values.append(val)
            v = values
        else:
            v = v[0]
        setattr(self, k, v)

    def dispose(self, key):
        """
        Deletes parameter key.
        :param key: string -> key you want to remove.
        """
        delattr(self, key)

    def dump(self):
        """
        Deletes all created parameters.
        """
        for attr in list(self()):
            delattr(self, attr)

    def __get_key(self):
        """
        Method used for obtaining system UUID for both nt and unix systems.
        Allows to decrypt data only on system where it was encrypted.
        :return: String
        """
        def create_key(key_input):
            """
            Extending 32 to 44 bytes using md5 salt, required by Fernet.
            """
            hard_key = (key_input[:16] + supersalt[16:32] + supersalt[:2] + supersalt[5:7] + key_input[7:9]
                        + supersalt[16:18] + key_input[21:23] + key_input[29] + "=")
            return hard_key.encode()

        # Converting salt string into md5 hash
        md5 = hashlib.md5()
        md5.update(self.__salt)
        supersalt = md5.hexdigest()

        if os.name == "nt":     # Windows compatibility.
            key = subprocess.check_output(['wmic', 'csproduct', 'get', 'UUID'], text=True) \
                .strip().splitlines()[2].replace("-", "")

            return create_key(key)
        elif os.name != "nt":   # Linux/UNIX compatibility.
            key = subprocess.check_output(['cat', '/sys/class/dmi/id/product_uuid'], text=True) \
                .strip().replace("-", "")
            return create_key(key)

    def veil(self, key, index="0", marker=""):
        """
        Encrypts created parameter.
        E.g.: for
        <instance>.create(pc1=["login", "password"])
        encrypting "password will be:
        <instance>.veil("pc1", 1)
        For dictionary value you can use either subkey or its index.
        :param key: string -> key containing value you want to encrypt
        :param index: string -> value index number(list) or key(dictionary)
        :param marker: String -> String with desired markers to put at beginning and end of veiled string. Single or
        multiple chars can be used. Multiple chars will be split into half;
        for uneven length - first char, content, rest of chars.
        """
        def mark(content, chars):
            if len(marker) == 0:
                return content
            elif len(chars) == 1:
                return chars + content + chars
            elif len(chars) > 1:
                if len(chars) % 2 == 0:
                    mid = len(chars) // 2
                    return chars[:mid] + content + chars[mid:]
                else:
                    return chars[:1] + content + chars[1:]

        values = self()[key]
        if isinstance(values, list):
            encrypted = Fernet(self.__get_key()).encrypt(values[int(index)].encode()).hex()
            values.pop(int(index))
            values.insert(int(index), mark(encrypted, marker))
            setattr(self, key, values)
        elif isinstance(values, dict):
            if index.isnumeric():
                encrypted = Fernet(self.__get_key()).encrypt(values[list(values)[int(index)]].encode()).hex()
                values[list(values)[int(index)]] = mark(encrypted, marker)
            else:
                encrypted = Fernet(self.__get_key()).encrypt(values[index].encode()).hex()
                values[index] = mark(encrypted, marker)
            setattr(self, key, values)
        else:
            encrypted = Fernet(self.__get_key()).encrypt(values.encode()).hex()
            setattr(self, key, mark(encrypted, marker))

    def unveil(self, encrypted_value):
        """
        Allows to decrypt values encrypted with create_pwd method.
        :param encrypted_value: String containing hexadecimal number.
        :return: String with decrypted password or "tooSalty".
        """
        try:
            soup = Fernet(self.__get_key()).decrypt(bytes.fromhex(encrypted_value)).decode()
        except Exception:
            soup = "tooSalty"
        return soup

    def save(self, verbose=False):
        """
        Saves created parameters to file (default: config.json in working directory)
        :param verbose: Any -> if not empty, prints result.
        :return: string - saving result
        """
        try:
            variables = {}
            with open(self.__fullpath, "w") as config:
                for k, v in self().items():
                    if k != "fullpath":
                        variables[k] = v
                json.dump(variables, config, indent=4)
            if verbose:
                print("{}CONFIG SAVE SUCCESS!{}".format(green, reset))
        except Exception as err:
            if verbose:
                print("{}CONFIG SAVE ERROR:{} {}".format(red, reset, err))

    def load(self, verbose=False):
        """
        Loads parameters from file and passes them to instance.
        :param verbose: Any -> if not empty, prints result.
        :return: string - loading result
        """
        if self.__check():
            with open(self.__fullpath, "r")as config:
                variables = json.load(config)
                for k, v in variables.items():
                    setattr(self, k, v)
                    if verbose:
                        print("{}CONFIG READ SUCCESS{}".format(green, reset))
        else:
            if verbose:
                print("{}CONFIG READ ERROR{}".format(red, reset))
