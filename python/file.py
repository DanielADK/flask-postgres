import mimetypes
import os
import time


class File:
    """
    File class to represent a file
    """
    def __init__(self, name: str, path: str):
        self.path = path
        self.name = name
        self.full_path = os.path.join(path, name)
        self.create_datetime = None
        self.size = None
        self.mimetype = None

    def get_mimetype(self) -> str:
        """
        Get the mimetype of the file
        :return: The mimetype of the file
        """
        if self.mimetype is None:
            suggest_type = mimetypes.guess_type(self.full_path)[0]
            self.mimetype = "unknown" if suggest_type is None else suggest_type
        return self.mimetype

    def get_size(self) -> int:
        """
        Get the size of the file
        :return: The size of the file
        """
        if self.size is None:
            self.size = os.stat(self.full_path).st_size
        return self.size

    def get_create_datetime_epoch(self) -> float:
        """
        Get the creation datetime of the file in epoch
        :return: The creation datetime of the file in epoch
        """
        if self.create_datetime is None:
            self.create_datetime = time.ctime(os.path.getctime(self.full_path))
        return self.create_datetime

    def get_create_datetime_iso(self) -> str:
        """
        Get the creation datetime of the file in ISO format
        :return: The creation datetime of the file in ISO format
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(str(self.get_create_datetime_epoch())))

    def __dict__(self) -> dict:
        """
        Get the dictionary representation of the file
        :return: The dictionary representation of the file
        """
        return {
            "name": self.name,
            "create_datetime": self.get_create_datetime_iso(),
            "size": self.get_size(),
            "mimetype": self.get_mimetype()
        }
