from django.conf import settings


def get_salesforce_domain():
    if hasattr(settings, "USE_SANDBOX") and settings.USE_SANDBOX:
        return "test"
    return "login"
