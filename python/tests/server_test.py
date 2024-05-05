import subprocess
import time

import pytest
import requests
import uuid
import os

test_files = {
    'test_file.txt': {
        'name': 'test_file.txt',
        'input': 'Lorem ipsum dolor sit amet.',
        'mimetype': 'text/plain',
        'create_datetime': ''
    },
    'test_image.jpg': {
        'name': 'test_image.jpg',
        'input': 'consectetur adipiscing elit.',
        'mimetype': 'image/jpeg',
        'create_datetime': ''
    },
    'test_document.pdf': {
        'name': 'test_document.pdf',
        'input': 'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
        'mimetype': 'application/pdf',
        'create_datetime': ''
    }
}

BASE_URL = 'http://localhost:5000'


@pytest.fixture(scope='module', autouse=True)
def start_server():
    global test_files, BASE_URL
    # Define the directory for test files
    test_files_dir = '../files'

    # Create the directory if it does not exist
    if not os.path.exists(test_files_dir):
        os.makedirs(test_files_dir)

    # Create some test files

    for file_name in test_files:
        file_data = test_files[file_name]
        # Create a file_name with random content
        with open(os.path.join(test_files_dir, file_data["name"]), 'w') as f:
            f.write(file_data['input'])
        epoch_time = time.ctime(os.path.getctime(os.path.join(test_files_dir, file_name)))
        iso_time = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(str(epoch_time)))
        test_files[file_name]['create_datetime'] = iso_time

    # Start the server
    server_process = subprocess.Popen(['python', '../server.py'])

    # Wait for the server to start listening
    time.sleep(1)

    yield

    # Terminate the server
    server_process.terminate()
    server_process.wait()

    # Remove the test files
    for file_name in test_files:
        os.remove(os.path.join(test_files_dir, file_name))


def test_get_file_stat_valid_uuid():
    global test_files
    # Iterate over all test files
    for file_name in test_files:
        file_data = test_files[file_name]
        # Generate a valid UUID
        valid_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, file_name))

        # Make a GET request to the /file/<uuid>/stat endpoint
        response = requests.get(f'{BASE_URL}/file/{valid_uuid}/stat')

        # Assert that the status code is 200
        assert response.status_code == 200
        parsed_response = response.json()

        # Assert that the mimetype, name and size are correct
        assert file_data['mimetype'] == parsed_response["mimetype"]
        assert file_data['name'] == parsed_response["name"]
        assert len(file_data["input"]) == parsed_response["size"]
        assert file_data['create_datetime'] == parsed_response["create_datetime"]


def test_get_file_stat_invalid_uuid():
    # Generate an invalid UUID
    invalid_uuid = 'invalid_uuid'

    # Make a GET request to the /file/<uuid>/stat endpoint
    response = requests.get(f'{BASE_URL}/file/{invalid_uuid}/stat')

    # Assert that the status code is 404
    assert response.status_code == 404


def test_read_file_valid_uuid():
    global test_files
    # Iterate over all test files
    for file_name in test_files:
        file_data = test_files[file_name]
        # Generate a valid UUID
        valid_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, file_name))

        # Make a GET request to the /file/<uuid>/read endpoint
        response = requests.get(f'{BASE_URL}/file/{valid_uuid}/read')

        # Assert that the status code is 200
        assert response.status_code == 200

        # Assert that the content is correct
        assert file_data['input'] == response.text


def test_read_file_invalid_uuid():
    # Generate an invalid UUID
    invalid_uuid = 'invalid_uuid'

    # Make a GET request to the /file/<uuid>/read endpoint
    response = requests.get(f'{BASE_URL}/file/{invalid_uuid}/read')

    # Assert that the status code is 404
    assert response.status_code == 404