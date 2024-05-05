import os
import uuid
import json
import mimetypes
from flask import Flask, Response
from file import File

app = Flask(__name__)
uuids = dict()
DIR = os.path.dirname(os.path.abspath(__file__))
FILES_PATH = os.path.join(DIR, "files")


@app.route('/file/<uuid_str>/stat', methods=['GET'])
def get_file_stat(uuid_str: str):
    global uuids, FILES_PATH
    # Get file
    file = uuids.get(uuid_str)
    if file is None:
        return json.dumps({"error": "File not found"}), 404

    # Create file object
    file_obj = File(file, FILES_PATH)
    return json.dumps(file_obj.__dict__()), 200


@app.route('/file/<uuid_str>/read', methods=['GET'])
def read_file(uuid_str: str):
    global uuids, FILES_PATH
    # Get file
    file = uuids.get(uuid_str)
    if file is None:
        return json.dumps({"error": "File not found"}), 404

    # Create file object
    file_obj = File(file, FILES_PATH)

    # Response object
    response = Response()
    response.headers["Content-Disposition"] = file_obj.name
    response.headers["Content-Type"] = file_obj.get_mimetype()

    # Read file and save to response
    with open(os.path.join(FILES_PATH, file), "r") as f:
        response.data = f.read()

    return response


def sync_uuids() -> None:
    """
    Sync UUIDs
    :return: None
    """
    global uuids, FILES_PATH
    # Get all files
    files = os.listdir(FILES_PATH)

    # Sync UUIDs
    for file in files:
        file_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, file)
        uuids[str(file_uuid)] = file


if __name__ == "__main__":
    # Get UUIDs from files
    sync_uuids()
    print("UUIDs:")
    for x in uuids:
        print(x, uuids[x])

    # Create the files directory if it does not exist
    if not os.path.exists(FILES_PATH):
        os.makedirs(FILES_PATH)

    # Run the app
    app.run(host='0.0.0.0', port=5000)
