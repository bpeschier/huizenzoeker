import requests

from .filters import filter_pool
from .exceptions import (FilterDoesNotExistError, APIError, ValidationError)

API_ENDPOINT = 'http://www.huizenzoeker.nl/api/v1/'

ORDER_TRANSLATION = {
    'new': 'nr',
    'construction_date': 'bj',
    'living_area': 'wov',
    'plot_area': 'pov',
    'price': 'pv',
    'distance': 'strl',
}

OBJECT_TYPE_TRANSLATION = {
    'sale': 'koop',
    'rent': 'huur',
}


class Huizenzoeker(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def for_rent(self, **kwargs):
        return self.objects(object_type='rent', **kwargs)

    def for_sale(self, **kwargs):
        return self.objects(object_type='sale', **kwargs)

    def objects(self, object_type='sale', **kwargs):
        # Default parameters
        params = {
            'sort': self._get_order(kwargs.pop('order_by', None)),
            'get': self._get_object_type(object_type),
        }

        # Add search filter parameters
        for key, value in kwargs.items():
            filter_name, *operation = key.split('__')
            if not operation:
                operation = ['exact']

            operation = operation[-1]  # let's see

            try:
                filter_obj = filter_pool[filter_name]
            except KeyError:
                raise FilterDoesNotExistError(
                    'Filter "{0}" does not exist, choose from {1}'.format(
                        filter_name, list(filter_pool.keys())))
            params.update(filter_obj.get_operation(operation, value))

        return self._request(params)

    def _request(self, params):
        params.update({
            'apisleutel': self.api_key,
            'output': 'json',
            'module': 'Objecten',
        })
        return self._parse(requests.get(API_ENDPOINT, params=params).json())

    @staticmethod
    def _parse(json_data):
        response = json_data['Response']

        if 'error' in response:
            raise APIError('Error in parameter "{parameter}": {bericht}'.format(**response['error']))
        else:
            return [Entry(e) for e in response['objecten']['object']]

    @staticmethod
    def _get_order(order):
        suffix = '-d' if order[0] == '-' else '-a'
        label = ORDER_TRANSLATION.get(order.strip('-'), 'nr')
        return label + suffix

    @staticmethod
    def _get_object_type(object_type):
        try:
            return OBJECT_TYPE_TRANSLATION[object_type]
        except KeyError:
            raise ValidationError('Object type "{object_type}" is not one of {options}',
                                  object_type=object_type, options=', '.join(OBJECT_TYPE_TRANSLATION.keys()))


class Entry(dict):
    #  TODO: translate dict into nice object
    pass