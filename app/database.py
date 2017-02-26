from peewee import *
import datetime
from os import environ
import time


db = None


def setup():
  global db
  db = PostgresqlDatabase(
    host=environ.get("DATABASE_HOST"),
    database=environ.get("DATABASE_DB"),
    user=environ.get("DATABASE_USER"),
    password=environ.get("DATABASE_PASSWORD")
  )

  def try_connect():
    try:
      db.connect()
    except OperationalError:
      if try_connect.num_tries < 5:
        time.sleep(5 * try_connect.num_tries)
        try_connect.num_tries += 1
        try_connect()
        return

      raise OperationalError(
        "Cannot connect to database. Retries failed."
      )
  try_connect.num_tries = 0
  try_connect()

  db.create_tables(
    [User, Measurement, UserSymptoms, UserRelatives],
    safe=True
  )


class Base(Model):
  class Meta:
    database = db


class User(Base):
  username = TextField(unique=True, index=True)
  password = CharField()
  full_name = TextField()
  join_time = DateTimeField(default=datetime.datetime.now)


class Measurement(Base):
  user = ForeignKeyField(User, index=True)
  value = DoubleField()
  record_time = DateTimeField(default=datetime.datetime.now, index=True)
  instrument = TextField(default="unlabeled")

  class Meta:
    primary_key = CompositeKey('user', 'instrument', 'record_time')


class UserSymptoms(Base):
  user = ForeignKeyField(User, index=True)
  symptom_name = TextField(index=True)
  add_time = DateTimeField(default=datetime.datetime.now)


class UserRelatives(Base):
  user = ForeignKeyField(User, index=True)
  full_name = TextField()
  phone = IntegerField()

  class Meta:
    primary_key = CompositeKey('user', 'phone')
