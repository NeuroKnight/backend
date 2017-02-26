from flask import Flask, jsonify, request
from app import database, user_controller


app = Flask(__name__)


def request_payload():
  """
  Obtain HTTP request POST/GET data body
  :return: key-value pairs
  """
  post_object = request.get_json(
    force=True,
    silent=True,
    cache=True
  )

  if post_object is None:
    post_object = {}

  get_object = request.args

  return dict(post_object.items() + get_object.items())


def response_execution(body_func, silence_errors=True):
  """
  Wrapper for execution of a route
  :param body_func: Route's function whose execution
    we should wrap over
  :param silence_errors: bool
  :return: Flask.Response
  """
  '''
  Any thrown exceptions are silenced into an HTTP >= 400
  '''
  if silence_errors:
    try:
      result = body_func()
    except BaseException as e:
      response = jsonify({
        'status': 400,
        'message': e.message,
        'data': {}
      })
      response.status_code = 400
      return response

    response = jsonify(result)
    response.status_code = result.get(
      "status",
      200
    )
    return response

  '''
  Any thrown exceptions are NOT silenced
  '''
  result = body_func()
  response = jsonify(result)
  response.status_code = result.get(
    "status",
    200
  )
  return response


@app.route("/api")
def route_home():
  return jsonify({
    'status': 200,
    'message': "Welcome to NeuroKnight's Backend API",
    'data': {}
  })


@app.route("/api/signup", methods=["POST", "GET"])
def route_user_register():
  def run():
    data = request_payload()
    return user_controller.signup(data)
  return response_execution(run)


@app.route("/api/login", methods=["POST", "GET"])
def route_user_login():
  def run():
    data = request_payload()
    return user_controller.login(data)
  return response_execution(run)


@app.route("/api/user/measurement", methods=["POST", "GET"])
def route_collect():
  def run():
    data = request_payload()
    return user_controller.measurement(data)
  return response_execution(run)


@app.route("/api/user/relative", methods=["POST", "GET"])
def route_user_relative():
  def run():
    data = request_payload()
    return user_controller.add_relative(data)
  return response_execution(run)


@app.route("/api/user/get_measurements", methods=["POST", "GET"])
def route_user_measurements():
  def run():
    data = request_payload()
    return user_controller.get_measurements(data)
  return response_execution(run)


print "Connecting to Server"
database.setup()
print "Database Connection Success"


if __name__ == "__main__":
  app.run()
