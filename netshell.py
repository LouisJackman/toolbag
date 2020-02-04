#!/usr/bin/env python3

from argparse import ArgumentParser
from functools import partial
import logging
import socket
import subprocess
from sys import exit, stderr
from textwrap import dedent
from threading import Thread
from time import sleep

NEW_LINE = "\n"
ENCODED_NEW_LINE = NEW_LINE.encode()
MAX_ATTEMPT = 5
BACKLOG = 1
ANYWHERE = "0.0.0.0"
MAX_RECV_BYTE_FRAGMENT = 1024 * 64


def start_server(port):
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    print("created server socket")

    attempted_port = port
    attempt = 0
    while True:
        try:
            server.bind((ANYWHERE, attempted_port))
            print(f"bound on {attempted_port}")
            break
        except OSError:
            print(f"failed to bind on port {attempted_port}; trying the next one")
            attempted_port += 1
            attempt += 1
            if MAX_ATTEMPT <= attempt:
                raise RuntimeError("tried too many times to bind but failed")

    server.listen(BACKLOG)
    print(f"listening with a backlog of {BACKLOG}")

    return server


class CommandAccumulator:

    def __init__(self, client):
        self._client = client
        self._accumulated = ""

    def next(self):
        while True:
            fragment = self._client.recv(MAX_RECV_BYTE_FRAGMENT)
            cmd = fragment.decode()
            if cmd == "":
                return None
            self._accumulated += cmd
            if NEW_LINE in self._accumulated:
                cmd, *rest = self._accumulated.split(NEW_LINE)
                self._accumulated = NEW_LINE.join(rest)
                return cmd.strip()


def send_client_command_feedback(client, process):
    stdout = process.stdout.decode()
    stderr = process.stderr.decode()
    feedback = dedent(f"""
        status: {process.returncode}
        stdout: {stdout}
        stderr: {stderr}
        """).lstrip()
    client.sendall(feedback.encode())


def respond_to_client(client):
    try:
        command_accumulator = CommandAccumulator(client)
        while True:
            client.sendall(">>> ".encode())
            cmd = command_accumulator.next()
            if cmd is None:
                break
            if len(cmd) <= 0:
                continue
            print(f"running cmd {cmd}...")
            process = subprocess.run(cmd, capture_output=True, shell=True)
            send_client_command_feedback(client, process)
            print("finished running cmd")

        # Some shells like to confusingly hide the last line of output without
        # trailing newlines.
        client.send(ENCODED_NEW_LINE)
    finally:
        client.close()


def main_loop(server):
    try:
        while True:
            print("awaiting new client")
            client, (client_host, client_port) = server.accept()
            print(f"handling client from {client_host} on port {client_port}")

            thread = Thread(
                name=f"handler-for-{client_host}",
                target=partial(respond_to_client, client),
            )
            thread.start()
            print(f"dispatched client handler")
    finally:
        server.close()


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--port", nargs="?", default=8080)
    return parser.parse_args()


def main():
    try:
        arguments = parse_args()
        server = start_server(arguments.port)
        main_loop(server)
    except KeyboardInterrupt:
        print("close requested; exiting")
    except Exception as exception:
        print(f"Error: {exception}", file=stderr)
        exit(1)


if __name__ == "__main__":
    main()

