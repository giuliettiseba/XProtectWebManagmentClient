"""
Gateway class used for calling the REST API.
"""
import json
import requests
import urllib3

# Remove the line below if verifying the certificate (which is recommended)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Gateway:
    """
    Class representing API Gateway.
    """
    def __init__(self, serverUrl: str):
        """Constructor

        :param server: The host name of the API Gateway, e.g. vms.example.com
        """
        self._serverUrl = serverUrl

    def get(self, session: requests.Session, resource_plural: str, token: str) -> str:
        """Retrieves a list of items.

        :param session: A requests.Session object which will be used for the duration of the
            integration to maintain logged-in state
        :param resource_plural: The name of the resource to access
        :param token: The bearer access token to use.

        :returns: String representation of the response body
        """
        url = self.__url(resource_plural)
        res = self.__request(session, 'GET', url, token)
        result = res.text
        return result

    def get_single(self, session: requests.Session, resource_plural: str, obj_id: str, token: str) -> str:
        """Retrieves a single item by id.

        :param session: A requests.Session object which will be used for the duration of the
            integration to maintain logged-in state.
        :param resource_plural: The name of the resource to access.
        :param obj_id: The id of the specific item to retrieve from the server.
        :param token: The bearer access token to use.

        :returns: String representation of the response body
        """
        url = self.__url(resource_plural, obj_id=obj_id)
        res = self.__request(session, 'GET', url, token)
        result = res.text
        return result

    def get_child_items(self, session: requests.Session, resource_plural: str, obj_id: str, child_item_type: str, token: str) -> str:
        """Gets a list of child items of a specific item.

        :param session: A requests.Session object which will be used for the duration of the
            integration to maintain logged-in state
        :param resource_plural: The name of the resource to access
        :param obj_id: The id of the specific item whose child items should be retrieved
        :param child_item_type: The item type of the child items to retrieve
        :param token: The bearer access token to use.

        :returns: String representation of the response body
        """
        url = self.__url(resource_plural, obj_id=obj_id, child_item_type=child_item_type)
        res = self.__request(session, 'GET', url, token)
        result = res.text
        return result

    def get_child_item_tasks(self, session: requests.Session, resource_plural: str, obj_id: str, child_item_type: str, token: str) -> dict:
        """Gets a list of tasks available on a specific child item type of a specific item

        :param session: A requests.Session object which will be used for the duration of the
            integration to maintain logged-in state
        :param resource_plural: The name of the resource to access
        :param obj_id: The id of the specific item whose child item tasks should be retrieved
        :param child_item_type: The item type of the child items for which to retrieve tasks
        :param token: The bearer access token to use.

        :returns: Parsed list of available tasks
        """
        url = self.__url(resource_plural, obj_id=obj_id, child_item_type=child_item_type)
        params = {
            'tasks' : 'true',
            'noData' : 'true'
        }
        res = self.__request(session, 'GET', url, token, params=params)
        result = res.text
        task_list = json.loads(result)['tasks']
        return task_list

    def get_tasks(self, session: requests.Session, resource_plural: str, token: str) -> list:
        """Gets a list of tasks available on a specific item type.

        :param session: A requests.Session object which will be used for the duration of the
            integration to maintain logged-in state.
        :param resource_plural: The name of the resource type to get tasks for.
        :param token: The bearer access token to use.

        :returns: Parsed list of available tasks
        """
        url = self.__url(resource_plural)
        params = {
            'tasks' : 'true',
            'noData' : 'true'
        }
        res = self.__request(session, 'GET', url, token, params=params)
        result = res.text
        task_list = json.loads(result)['tasks']
        return task_list

    def perform_task(self, session: requests.Session, resource_plural: str, obj_id: str, task: str, payload: str, token: str) -> str:
        """Invokes a task on a specific item. 

        Technically invokes a task asynchronously, which may then be retrieved using the
        resource_plural "tasks" and the id supplied in the response.

        :param session: A requests.Session object which will be used for the duration of the
            integration to maintain logged-in state
        :param resource_plural: The name of the resource type of the object
        :param obj_id: The id of the object on which the task will be performed
        :param task: The id (e.g. getDevicePresets) of the task to perform
        :param payload: A JSON string representing the payload of the request
        :param token: The bearer access token to use.

        :returns: String representation of the response body
        """
        url = self.__url(resource_plural, obj_id=obj_id)
        params = {
            'task': task
        }
        res = self.__request(session, 'POST', url, token, params=params, payload=payload)
        result = res.text
        return result

    def perform_child_task(self, session: requests.Session, resource_plural: str, obj_id: str, child_item_type: str, task: str, payload: str, token: str) -> str:
        """Performs a child item type based task on a specific item.

        Technically starts a task asynchronously, which may then be retrieved using the
        resource_plural "tasks" and the id supplied in the response.

        :param session: A requests.Session object which will be used for the duration of the
            integration to maintain logged-in state.
        :param resource_plural: The name of the resource type of the object.
        :param obj_id: The id of the object on whose child items the task should be performed.
        :param child_item_type: The child item type on which to perform the task.
        :param task: The id of the task to be performed.
        :param payload: JSON string representation of the request body.
        :param token: The bearer access token to use.

        :returns: String representation of the response body.
        """
        url = self.__url(resource_plural, obj_id=obj_id, child_item_type=child_item_type)
        params = {
            "task": task
        }
        
        res = self.__request(session, 'POST', url, token, params=params, payload=payload)
        result = res.text
        return result

    def create_item(self, session: requests.Session, resource_plural: str, payload: str, token: str) -> str:
        """Creates an item on the server.

        :param session: A requests.Session object which will be used for the duration of the
            integration to maintain logged-in state
        :param resource_plural: The name of the resource type of the object
        :param payload: A JSON string representing the payload of the request
        :param token: The bearer access token to use

        :returns: A string containing the JSON representation of the created item
        """
        url = url = self.__url(resource_plural)
        res = self.__request(session, 'POST', url, token, payload=payload)
        result = res.text
        return result

    def update_item(self, session: requests.Session, resource_plural: str, payload: str, obj_id: str, token: str) -> str:
        """Updates an item.

        :param session: A requests.Session object which will be used for the duration of the
            integration to maintain logged-in state
        :param resource_plural: The name of the resource type of the object
        :param payload: A JSON string representing the payload of the request
        :param obj_id: The id of the item to update
        :param token: The bearer access token to use

        :returns: A string containing the JSON representation of the updated item
        """
        url = url = self.__url(resource_plural, obj_id=obj_id)
        res = self.__request(session, 'PUT', url, token, payload=payload)
        result = res.text
        return result

    def delete_item(self, session: requests.Session, resource_plural: str, obj_id: str, token: str) -> str:
        """Deletes an item.

        :param session: A requests.Session object which will be used for the duration of
            the integration to maintain logged-in state
        :param resource_plural: The name of the resource type of the object
        :param obj_id: The id of the object to delete
        :param token: The bearer access token to use

        :returns: A status message
        """
        url = self.__url(resource_plural, obj_id=obj_id)
        res = self.__request(session, 'DELETE', url, token)
        result = res.text
        return result

    def __request(self, session: requests.Session, verb: str, url: str, token: str, params: dict = {}, payload: str = '') -> requests.Response:
        """Submits request through session using bearer token.

        :param session: A requests.Session object which will be used for the duration of
            the integration to maintain logged-in state
        :param verb: Request method
        :param url: Request URI
        :param token: The bearer access token to use
        :param params: Request parameters as a dict
        :param payload: Request body as a string

        :returns: requests.Response object
        """
        tokenstring = 'Bearer ' + token
        headers = {
            'Authorization': tokenstring
        }
        # Replace verify=False below with this instead to verify the certificate:
        #   verify='path/to/certificate'
        return session.request(verb, url, headers=headers, params=params, data=payload, verify=False)

    def __url(self, resource_plural: str, obj_id: str = None, child_item_type: str = None):
        """Formats request URI.

        :param resource_plural: The name of the resource type
        :param obj_id: Optional id of object
        :param child_item_type: Optional child item type
        """
        result = f'{self._serverUrl}/api/rest/v1/{resource_plural}'
        if obj_id is not None:
            result += '/' + obj_id
        if child_item_type is not None:
            result += '/' + child_item_type
        return result
