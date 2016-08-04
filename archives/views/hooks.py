import httplib

from flask import abort
from flask import request

from archives import app
from archives import task


@app.route('/hook', methods=['POST'])
def hook():
    if not request.is_json:
        abort(httplib.BAD_REQUEST)

    info = request.get_json()
    ref = info.get('ref')

    # TODO(benjamin): filter branch
    if ref != 'refs/heads/master':
        return "Not Changed"

    repository = info.get('repository').get('git_http_url')
    user_name = info.get('user_name')
    user_email = info.get('user_email')

    task.build.delay(app.config.get('BUILD_BRANCH'), user_name, user_email, repository)

    return "Success"
