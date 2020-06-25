import requests

from django.utils.crypto import get_random_string


class OAuth:
    def __init__(self, token_data):
        self.token_data = token_data
        self.salesforce_user = self._get_salesforce_user()
        self._password = get_random_string(length=16)

    def _get_salesforce_user(self):
        sf_id_url = self.token_data.get("id")
        access_token = self.token_data.get("access_token")
        response = requests.get(
            sf_id_url, headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json()

    @property
    def username(self):
        return self.salesforce_user.get("username")

    @property
    def password(self):
        return self._password

    @property
    def email(self):
        return self.salesforce_user.get("email")
