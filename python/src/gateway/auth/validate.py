import os, requests


def token(request):
    if not "Authorization" in request.headers:
        return None, ("missing credentials", 401)

    token = request.headers["Authorization"]

    if not token:
        return None, ("missing credentials", 401)

  # ! passing the authorization token to the  validation in our auth service 
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token},
    )

    if response.status_code == 200:
          # ! this will contain the access of the Bearer token
        return response.text, None
    else:
        return None, (response.text, response.status_code)