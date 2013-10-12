import re
from .exceptions import ValidationError

filter_pool = {}


class FilterBase(type):
    def __new__(mcs, name, bases, attrs):
        filter_name = attrs.get('name', False)
        cls = type.__new__(mcs, name, bases, attrs)
        if filter_name and filter_name not in filter_pool:
            filter_pool[filter_name] = cls()
        return cls


class Filter(metaclass=FilterBase):
    key = None

    def get_operation(self, operation, value):
        operation_func = getattr(self, operation, False)
        if not operation_func:
            raise NotImplementedError('{operation} not implemented for {filter}'.format(
                operation=operation, filter=str(self)))
        elif self.validate(value, operation):
            return operation_func(value)

    def exact(self, value):
        return {
            self.key: value
        }

    def validate(self, value, operation):
        """
        Checks the value for the specific filter
        """
        raise NotImplementedError


class RangeFilter(Filter):
    @property
    def key_low(self):
        return self.key[0]

    @property
    def key_high(self):
        return self.key[1]

    def exact(self, value):
        return {
            self.key_low: value,
            self.key_high: value,
        }

    def between(self, value):
        return {
            self.key_low: value[0],
            self.key_high: value[1],
        }

    def gte(self, value):
        return {
            self.key_low: value,
        }

    def lte(self, value):
        return {
            self.key_high: value,
        }

    def validate(self, value, operation):
        if operation == 'between' and (not isinstance(value, list) or len(value) != 2 or not all([isinstance(v, int) for v in value])):
            raise ValidationError('{filter} needs a minimum and a maximum'.format(filter=self.__class__.__name__))
        elif operation != 'between' and not isinstance(value, int):
            raise ValidationError('{filter} needs an integer'.format(filter=self.__class__.__name__))
        return True


class ProvinceFilter(Filter):
    PROVINCES = ('NH', 'ZH', 'UT', 'FR', 'GR', 'DR', 'OV', 'GE', 'NB', 'LB', 'ZE',)
    name = "province"
    key = "provincie"

    def validate(self, value, operation):
        if value not in self.PROVINCES:
            raise ValidationError('Province should be one of {provinces}'.format(provinces=self.PROVINCES))
        return True


class CountyFilter(Filter):
    name = "county"
    key = "gemeente"

    def validate(self, value, operation):
        return True  # Could be anything


class CityFilter(Filter):
    name = "city"
    key = "plaats"

    def validate(self, value, operation):
        return True  # Could be anything


class NeighborhoodFilter(Filter):
    name = "neighborhood"
    key = "wijk"

    def validate(self, value, operation):
        return True  # Could be anything


class ZipcodeFilter(Filter):
    name = "zipcode"
    key = "pc"

    def validate(self, value, operation):
        if not re.match('\d{4}([A-Z]{2})?', value):
            raise ValidationError('Zipcode should be either 4 digits or 4 digits and 2 letters')
        return True


class MinimumRoomsFilter(Filter):
    name = "minimum_rooms"
    key = "ka"

    def validate(self, value, operation):
        if not isinstance(value, int) and not re.match('\d+', value):
            raise ValidationError('Minimum rooms should be a positive number')
        return True


class DaysPublishedFilter(Filter):
    name = "days_published"
    key = "anbd"

    def validate(self, value, operation):
        if not isinstance(value, int) and not re.match('\d+', value):
            raise ValidationError('Days published should be a positive number')
        return True


class PriceFilter(RangeFilter):
    name = "price"
    key = ["pv", "pt"]


class LivingAreaFilter(RangeFilter):
    name = "living_area"
    key = ["wov", "wot"]


class PlotAreaFilter(RangeFilter):
    name = "plot"
    key = ["pov", "pot"]


class ConstructionDateFilter(RangeFilter):
    name = "construction_date"
    key = ["bjv", "bjt"]
