# Rest framework imports
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict


def response(status: bool, message: str, status_code: int, data=None, headers=None):
    """
    Customize the response for better information delivery.

    :param status: True if the response if for successful api response else False
    :param message: String message to give details
    :param status_code: states code of the response
    :param data: send data if any
    :param headers: provide headers in the response
    :return: Response class object
    """
    if headers is None:
        headers = {}

    message = message if type(message) in [ReturnDict, list] else {message}

    return Response(data if data else message, status=status_code, headers=headers)
