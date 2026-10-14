"""Supervise CLI work in a child so even a blocking regex has a deadline."""
import multiprocessing
import time

from .common import ProfileError, ResourceError
from .pipeline import generate_bundle, preserve_failed_run, validate_bundle
from .profile import inspect_profile, load_profile


def worker(connection, command, profile, location):
    try:
        if not isinstance(profile, dict):
            profile = load_profile(profile)
        connection.send(("ready", profile["generation"]["limits"]["timeout_seconds"]))
        if command == "inspect":
            result = inspect_profile(profile)
        elif command == "generate":
            result = generate_bundle(profile, location, on_start=lambda staging, target:
                                     connection.send(("started", staging, target)))
        else:
            result = validate_bundle(profile, location)
        connection.send(("done", result))
    except BaseException as error:
        connection.send(("error", isinstance(error, ProfileError),
                         "interrupted" if isinstance(error, KeyboardInterrupt) else str(error)))
    finally:
        connection.close()


def run_isolated(command, profile, location):
    context = multiprocessing.get_context("spawn")
    receive, send = context.Pipe(duplex=False)
    process = context.Process(target=worker, args=(send, command, profile, location))
    process.start()
    send.close()
    deadline = time.monotonic() + 10  # bounded interpreter startup, separate from the work budget
    started = None
    complete = False
    failure = "interrupted"
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ResourceError("execution timeout exceeded")
            if not receive.poll(min(0.05, remaining)):
                if not process.is_alive():
                    raise ResourceError("worker exited without a result")
                continue
            try:
                message = receive.recv()
            except EOFError as error:
                raise ResourceError("worker exited without a result") from error
            if message[0] == "ready":
                deadline = time.monotonic() + message[1]
            elif message[0] == "started":
                started = message[1:]
            elif message[0] == "error":
                raise (ProfileError if message[1] else ResourceError)(message[2])
            elif message[0] == "done":
                if time.monotonic() > deadline:
                    raise ResourceError("execution timeout exceeded")
                complete = True
                return message[1]
    except BaseException as error:
        failure = "interrupted" if isinstance(error, KeyboardInterrupt) else str(error)
        raise
    finally:
        if process.is_alive():
            process.terminate()
        process.join(timeout=0.5)
        if process.is_alive():
            process.kill()
            process.join(timeout=0.5)
        # A very short deadline may expire before the parent's first 'started' read.
        try:
            while receive.poll():
                message = receive.recv()
                if message[0] == "started":
                    started = message[1:]
        except EOFError:
            pass
        receive.close()
        if not complete and started:
            preserve_failed_run(*started, failure)
