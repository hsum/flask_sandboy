"""Various utilities for augmenting SQLAlchemy models."""

import datetime
from functools import wraps

from flask import request

from flask_sandboy.exception import ForbiddenException, BadRequestException


class SerializableModel(object):
    """A SQLAlchemy model mixin class that can serialize itself as JSON."""

    def to_dict(self):
        """Return dict representation of class by iterating over database
        columns."""
        value = {}
        for column in self.__table__.columns:
            attribute = getattr(self, column.name)
            if isinstance(attribute, datetime.datetime):
                attribute = str(attribute)
            value[column.name] = attribute
        return value

    def from_dict(self, attributes):
        """Update the current instance based on attribute->value items in
        *attributes*."""
        for attribute in attributes:
            setattr(self, attribute, attributes[attribute])
        return self


def verify_fields(function):
    """A decorator to automatically verify all required JSON fields
    have been sent."""
    @wraps(function)
    def decorated(instance, *args, **kwargs):
        """The decorator function."""
        data = request.get_json(force=True, silent=True)
        if not data:
            raise BadRequestException("No data received from request")
        for required in instance.__model__.__table__.columns:
            if required.name in (
                    instance.__model__.__table__.primary_key.columns) or required.default or required.nullable is True:
                continue
            if required.name not in data:
                raise ForbiddenException('{} required'.format(required))
        return function(instance, *args, **kwargs)

    return decorated
