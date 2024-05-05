import argparse
import sys
import requests


def stat_command(args: argparse.Namespace) -> None:
    """
    Stat command implementation
    :param args:
    :return:
    """
    # Check the backend
    if args.backend == 'grpc':
        print(f'gRPC backend is not implemented')
        return

    # Call the REST endpoint
    url = f"{try_repair_url(args.base_url)}file/{args.uuid}/stat"
    print(f'Stat command called with UUID: {args.uuid}')
    response = rest_call_endpoint(url)
    send_to_output(args.output, response)


def read_command(args: argparse.Namespace) -> None:
    """
    Read command implementation
    :param args:
    :return:
    """
    # Check the backend
    if args.backend == 'grpc':
        print(f'gRPC backend is not implemented')
        return

    # Call the REST endpoint
    print(f'Read command called with UUID: {args.uuid}')
    url = f"{try_repair_url(args.base_url)}file/{args.uuid}/read"
    response = rest_call_endpoint(url)
    send_to_output(args.output, response)


def try_repair_url(base_url: str) -> str:
    """
    Try to repair the URL by adding a trailing slash
    :param base_url:
    :return:
    """
    return base_url if base_url.endswith('/') else base_url + '/'


def rest_call_endpoint(endpoint: str) -> str:
    """
    Call the REST endpoint
    :param endpoint:
    :return:
    """
    response = requests.get(endpoint)
    return response.text


def send_to_output(output: str, content: str) -> None:
    """
    Send the content to the output
    :param output:  file or dash for stdout
    :param content: content to be saved
    :return:
    """
    if output == '-':
        print(content)
    else:
        with open(output, 'w') as f:
            f.write(content)
        print(f'Output saved to {output}')

# Create the parser
parser = argparse.ArgumentParser(prog='file-client', description='CLI application for file operations')

subparsers = parser.add_subparsers()

# Stat command
stat_parser = subparsers.add_parser('stat', help='Prints the file metadata in a human-readable manner.')
stat_parser.add_argument('uuid', help='UUID of the file')
stat_parser.set_defaults(func=stat_command)

# Read command
read_parser = subparsers.add_parser('read', help='Outputs the file content.')
read_parser.add_argument('uuid', help='UUID of the file')
read_parser.set_defaults(func=read_command)

# Common arguments
parser.add_argument('--backend', choices=['grpc', 'rest'], default='grpc', help='Set a backend to be used')
parser.add_argument('--grpc-server', default='localhost:50051', help='Set a host and port of the gRPC server')
parser.add_argument('--base-url', default='http://localhost/', help='Set a base URL for a REST server')
parser.add_argument('--output', default='-', help='Set the file where to store the output')

# Parse the arguments
args = parser.parse_args()

# Check if the function is set
if 'func' not in args:
    parser.print_help(sys.stderr)
    sys.exit(1)
# Call the function
args.func(args)
