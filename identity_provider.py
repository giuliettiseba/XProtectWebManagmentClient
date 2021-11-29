"""
Function for getting an access token for the REST API.
"""
import requests

def get_token(session: requests.Session, username: str, password: str, serverUrl: str) -> str:
    """
    Requests an OAuth 2.0 access token from the identity provider on the specified server for a given VMS user.

    :param session: A requests.Session object which will be used for the duration of the
        integration to maintain logged-in state
    :param username: The username of an XProtect basic user with the XProtect Administrators role
    :param password: The password of the user logging in
    :param server: The hostname of the machine hosting the identity provider, e.g. "vms.example.com"

    :returns: Access token as a JSON object. The value of the 'access_token' property is the bearer token.

        Note the "expires_in" property; if you're planning on making a larger integration, you will
        have to renew before it has elapsed.
    """
    url = f'{serverUrl}/IDP/connect/token'
    payload = f'grant_type=password&username={username}&password={password}&client_id=GrantValidatorClient'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    res = session.request("POST", url, headers=headers, data=payload, verify=False)

    response = res.text

    return response
