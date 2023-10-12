import urllib

import requests

from s3i.exception import S3IDittoError, raise_error_from_response


def query_all(fn):
    """Adds pagination to a request.

    Expects a function, that returns a rest get request without the keyword "cursor".
    Returns a list of json objects, that meet the query.

    :param fn: Function returning a rest get request
    :type fn: function
    """
    def inner(*args, **kwargs):
        url, headers = fn(*args, **kwargs)
        response = requests.get(url, headers=headers)
        response_json = raise_error_from_response(response, S3IDittoError, 200)
        results = response_json["items"]
        cursor = response_json.get("cursor", None)
        while cursor:
            response = requests.get(url,
                                    headers=headers,
                                    params={"option": f"cursor({cursor})"})
            response_json = raise_error_from_response(response, S3IDittoError, 200)
            items = response_json["items"]
            results += items
            cursor = response_json.get("cursor", None)
        return results

    return inner

def http_error_from_request_response(response):
    """Returns an urllib.error.HTTPError created from a requests.Response
    object.

    :type response: requests.Response
    :rtype: urllib.error.HTTPError

    """
    error = urllib.error.HTTPError(
        code=response.status_code,
        msg=response.text,
        hdrs=response.headers,
        fp=None,
        url=response.url,
    )
    return error
