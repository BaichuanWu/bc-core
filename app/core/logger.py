from sentry_sdk import capture_exception

def logger_exception(e):
    return capture_exception(e)