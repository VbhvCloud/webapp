# Rest framework imports
from rest_framework.response import Response


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
    return Response({
        "status": "success" if status else "error",
        "message": message,
        "data": data if status else None
    }, status=status_code, headers=headers)
