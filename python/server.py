import os
import uuid
import json
import mimetypes
from flask import Flask, Response
from file import File

app = Flask(__name__)
uuids = dict()
PATH = "./files"


@app.route('/file/<uuid_str>/stat', methods=['GET'])
def get_file_stat(uuid_str: str):
    global uuids, PATH
    # Get file
    file = uuids.get(uuid_str)
    if file is None:
        return json.dumps({"error": "File not found"}), 404

    # Create file object
    file_obj = File(file, PATH)
    return json.dumps(file_obj.__dict__()), 200


@app.route('/file/<uuid_str>/read', methods=['GET'])
def read_file(uuid_str: str):
    global uuids, PATH
    # Get file
    file = uuids.get(uuid_str)
    if file is None:
        return json.dumps({"error": "File not found"}), 404

    # Create file object
    file_obj = File(file, PATH)

    # Response object
    response = Response()
    response.headers["Content-Disposition"] = file_obj.name
    response.headers["Content-Type"] = file_obj.get_mimetype()

    # Read file and save to response
    with open(os.path.join(PATH, file), "r") as f:
        response.data = f.read()

    return response


def sync_uuids() -> None:
    """
    Sync UUIDs
    :return: None
    """
    global uuids, PATH
    # Get all files
    files = os.listdir(PATH)

    # Sync UUIDs
    for file in files:
        file_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, file)
        uuids[str(file_uuid)] = file


if __name__ == "__main__":
    sync_uuids()
    print("UUIDs:")
    for x in uuids:
        print(x, uuids[x])
    app.run(host='0.0.0.0', port=5000)
