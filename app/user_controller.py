from cerberus import Validator
import database
from datetime import datetime
from playhouse.shortcuts import model_to_dict


def signup(payload):
  schema = Validator({
        'username': {
          'type': 'string',
          'required': True
        },
        'password': {
          'type': 'string',
          'required': True
        },
        'full_name': {
          'type': 'string',
          'required': True
        }
      })

  if not schema.validate(payload):
    return {
      'status': 400,
      'data': schema.errors,
      'message': 'Payload incorrect/missing values'
    }

  database.User.create(
    username=payload.get('username'),
    password=payload.get('password'),
    full_name=payload.get('full_name')
  )

  return {
    'status': 200,
    'data': {},
    'message': 'success'
  }


def login(payload):
  schema = Validator({
    'username': {
      'type': 'string',
      'required': True
    },
    'password': {
      'type': 'string',
      'required': True
    }
  })

  if not schema.validate(payload):
    return {
      'status': 400,
      'data': schema.errors,
      'message': 'Payload incorrect/missing values'
    }

  try:
    user = database.User.select().where(
      database.User.username == payload.get("username"),
      database.User.password == payload.get("password")
    ).get()
  except database.User.DoesNotExist:
    return {
      'status': 400,
      'data': {},
      'message': 'User does not exist'
    }

  result = model_to_dict(user)

  result["join_time"] = (
    result["join_time"] - datetime(1970, 1, 1)
  ).total_seconds()

  return {
    'status': 200,
    'data': {
      'token': result["id"]
    },
    'message': 'success'
  }


def measurement(payload):
  schema = Validator({
    'token': {
      'type': 'string',
      'required': True
    },
    'value': {
      'type': 'string',
      'required': True
    },
    'instrument': {
      'type': 'string',
      'required': True
    }
  })

  if not schema.validate(payload):
    return {
      'status': 400,
      'data': schema.errors,
      'message': 'Payload incorrect/missing values'
    }

  try:
    new_measurement = database.Measurement()
    new_measurement.user = payload["token"]
    new_measurement.value = payload["value"]
    new_measurement.instrument = payload["instrument"]

    if payload.get("record_time") is not None:
      new_measurement.record_time = payload["record_time"]

    new_measurement.save()
  except database.User.DoesNotExist:
    return {
      'status': 400,
      'data': {},
      'message': "Invalid token: User does not exist"
    }

  return {
    'status': 200,
    'data': {},
    'message': 'success'
  }


def add_relative(payload):
  schema = Validator({
    'token': {
      'type': 'string',
      'required': True
    },
    'full_name': {
      'type': 'string',
      'required': True
    },
    'phone': {
      'type': 'string',
      'required': True
    }
  })

  if not schema.validate(payload):
    return {
      'status': 400,
      'data': schema.errors,
      'message': 'Payload incorrect/missing values'
    }

  try:
    new_relative = database.UserRelatives()
    new_relative.user = payload["token"]
    new_relative.full_name = payload["full_name"]
    new_relative.phone = payload["phone"]
    new_relative.save()
  except database.User.DoesNotExist:
    return {
      'status': 400,
      'data': {},
      'message': 'Invalid Token: User does not exist'
    }

  return {
    'status': 200,
    'data': {},
    'message': 'success'
  }


def get_measurements(payload):
  schema = Validator({
    'token': {
      'type': 'string',
      'required': True
    },
    'instrument': {
      'type': 'string',
      'required': False
    }
  })

  if not schema.validate(payload):
    return {
      'status': 400,
      'data': {},
      'message': 'Token required'
    }

  try:
    measurements = database.Measurement.select().where(
      database.Measurement.instrument == payload.get("instrument"),
      database.Measurement.user == payload.get("token")
    )
  except database.User.DoesNotExist:
    return {
      'status': 400,
      'data': {},
      'message': 'Invalid Token - User does not exist'
    }

  results = [{'instrument': measurement_obj.instrument,
              'value': measurement_obj.value,
              'record_time': (
                measurement_obj.record_time - datetime(1970, 1, 1)
              ).total_seconds()}
             for measurement_obj in measurements]

  return {
    'status': 200,
    'data': {
      'results': results
    },
    'message': 'success'
  }
