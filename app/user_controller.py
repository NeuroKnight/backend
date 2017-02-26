from cerberus import Validator
import database
from datetime import datetime
from playhouse.shortcuts import model_to_dict
from twilio.rest import TwilioRestClient
from os import environ


twilio_client = TwilioRestClient(
  environ.get("TWILIO_API_ID"),
  environ.get("TWILIO_API_KEY")
)


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
      'status': 410,
      'data': schema.errors,
      'message': 'Payload incorrect/missing values'
    }

  try:
    new_measurement = database.Measurement()
    new_measurement.user = int(payload.get("token"))
    new_measurement.value = float(payload.get("value"))
    new_measurement.instrument = payload.get("instrument")

    if payload.get("record_time") is not None:
      new_measurement.record_time = payload.get("record_time")

    if new_measurement.save(force_insert=True) == 1:
      return {
        'status': 200,
        'data': {},
        'message': 'success'
      }
    return {
      'status': 402,
      'data': {},
      'message': 'Did not save data'
    }

  except database.User.DoesNotExist:
    return {
      'status': 401,
      'data': {},
      'message': "Invalid token: User does not exist"
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
    new_relative.user = int(payload.get("token"))
    setattr(new_relative, "full_name", payload.get("full_name"))
    new_relative.phone = int(payload.get("phone"))

    twilio_client.messages.create(
      to=("+" + payload.get("phone")),
      from_="+3059514410",
      body="You were added to %s contacts for NightWatch"
           % new_relative.user.full_name
    )

    if new_relative.save(force_insert=True) == 1:
      return {
        'status': 200,
        'data': {},
        'message': 'success'
      }
    return {
      'status': 400,
      'data': {},
      'message': 'Did not save data'
    }

  except database.User.DoesNotExist:
    return {
      'status': 400,
      'data': {},
      'message': 'Invalid Token: User does not exist'
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
      'data': schema.errors,
      'message': 'Invalid input'
    }

  try:
    if payload.get("instrument"):
      measurements = database.Measurement.select().where(
        database.Measurement.instrument == payload.get("instrument"),
        database.Measurement.user == payload.get("token")
      )
    else:
      measurements = database.Measurement.select().where(
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


def get_relatives(payload):
  schema = Validator({
    'token': {
      'type': 'string',
      'required': True
    }
  })

  if not schema.validate(payload):
    return {
      'status': 400,
      'data': schema.errors,
      'message': 'Invalid input'
    }

  try:
    relatives = database.UserRelatives.select().where(
      database.UserRelatives.user == payload.get("token")
    )
  except database.User.DoesNotExist:
    return {
      'status': 400,
      'data': {},
      'message': 'Invalid Token - User does not exist'
    }

  results = [{'full_name': relative.full_name,
              'phone': relative.phone}
             for relative in relatives]

  return {
    'status': 200,
    'data': {
      'results': results
    },
    'message': 'success'
  }
