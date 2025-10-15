from __future__ import annotations
__all__ = [
    'Config', 'Variable', 'StrVar', 'IntVar', 'EnumVar', 'FloatVar', 'BoolVar', 'TextChannelVar', 'RoleVar', 'ListVar'
]
from typing import Any, Type, Self, TYPE_CHECKING
from abc import ABC, abstractmethod
import json

from db import db

if TYPE_CHECKING:
    from enum import IntEnum
    from . import Guild


class Variable(ABC):
    """ Base variable class """
    _type: Type
    notnull: bool
    default: Any

    @abstractmethod
    def validate(self, guild: Guild, new_value: Any):
        pass

    def _validate_type(self, new_value):
        if new_value is None:
            if self.notnull:
                raise ValueError("This variable can't be unset.")
            return

        if type(new_value) is not self._type:
            raise ValueError(f'Invalid type, expected {self._type}, got {type(new_value)}.')


class StrVar(Variable):
    """ Base string variable """
    _type = str

    def __init__(self, default: str = None, notnull: bool = False, max_length: int = 1024, min_length: int = 0):
        self.default = default
        self.notnull = notnull
        self.max_length = max_length
        self.min_length = min_length

    def validate(self, guild: Guild, new_value: Any):
        self._validate_type(new_value)
        if new_value is None:
            return
        if len(new_value) > self.max_length:
            raise ValueError(f'Must be <= than {self.max_length} characters.')
        if len(new_value) < self.min_length:
            raise ValueError(f'Must be >= than {self.min_length} characters.')


class IntVar(Variable):
    """ Base string variable """
    _type = int

    def __init__(self, default: int = None, notnull: bool = False, max_value: int = None, min_value: int = None):
        self.default = default
        self.notnull = notnull
        self.max_value = max_value
        self.min_value = min_value

    def validate(self, guild: Guild, new_value: Any):
        self._validate_type(new_value)
        if new_value is None:
            return
        if self.max_value is not None and new_value > self.max_value:
            raise ValueError(f'Must be <= {self.max_value}.')
        if self.min_value is not None and new_value < self.min_value:
            raise ValueError(f'Must be >= {self.min_value}.')


class EnumVar(Variable):
    _type = int

    def __init__(self, enum_cls: IntEnum.__class__, default: int = None, notnull: bool = False):
        self.default = default
        self.notnull = notnull
        self.enum_cls = enum_cls

    def validate(self, guild: Guild, new_value: Any):
        self._validate_type(new_value)
        if new_value is None:
            return
        try:
            self.enum_cls(new_value)
        except ValueError:
            raise ValueError('Incorrect value')


class FloatVar(Variable):
    _type = float

    def __init__(self, default: float = None, notnull: bool = False, max_value: float = None, min_value: float = None):
        self.default = default
        self.notnull = notnull
        self.max_value = max_value
        self.min_value = min_value

    def validate(self, guild: Guild, new_value: Any):
        self._validate_type(new_value)
        if new_value is None:
            return
        if self.max_value is not None and new_value > self.max_value:
            raise ValueError(f'Must be <= {self.max_value}')
        if self.min_value is not None and new_value < self.min_value:
            raise ValueError(f'Must be >= {self.min_value}')


class BoolVar(Variable):
    """ Base string variable """
    _type = bool

    def __init__(self, default: bool = None, notnull: bool = False):
        self.default = default
        self.notnull = notnull

    def validate(self, guild: Guild, new_value: Any):
        self._validate_type(new_value)


class TextChannelVar(Variable):
    """ Text channel id """
    _type = str
    default = None
    notnull = False

    def __init__(self, channel_type: int = None):
        self.channel_type = channel_type

    def validate(self, guild: Guild, new_value: Any):
        self._validate_type(new_value)
        if new_value is None:
            return
        if new_value not in guild.channels.keys():
            raise ValueError(f'Channel with id {new_value} not found on the server.')
        if guild.channels[new_value].type != 0:
            raise ValueError(f'Channel "{guild.channels[new_value].name}" is not a text channel.')
        return


class RoleVar(Variable):
    """ Text channel id """
    _type = str
    default = None
    notnull = False

    def validate(self, guild: Guild, new_value: Any):
        self._validate_type(new_value)
        if new_value is None:
            return
        if new_value not in guild.roles.keys():
            raise ValueError(f'Role with id {new_value} not found on the server.')
        return


class ListVar(Variable):
    _type = list

    def __init__(self, variables: dict[str, Variable], default: list[dict] = None, notnull: bool = True):
        self.variables = variables
        self.default = default if default is not None else []
        self.notnull = notnull

    def validate(self, guild: Guild, new_value: Any):
        self._validate_type(new_value)
        if new_value is None:
            return
        try:
            for count, row in enumerate(new_value):
                for name, variable in self.variables.items():
                    variable.validate(guild, row[name])
        except Exception as e:
            raise ValueError(f"Error at row number {count+1}, sub-variable '{name}': {str(e)}")


class Config:
    _table_name: str
    _name: str
    _variables: dict[str: Variable] = {}

    def __init__(self, data: dict, p_key, f_key=None):
        self._p_key = p_key
        self._f_key = f_key
        for key in self._variables.keys():
            self.__setattr__(key, data.get(key, self._variables[key].default))

    def __repr__(self):
        return f'<Config {self.__class__.__name__} p_key={self._p_key} f_key={self._f_key}>'

    def __dict__(self):
        return {key: self.__getattribute__(key) for key in self._variables.keys()}

    @classmethod
    async def create(cls, p_key: int = None, f_key: int = None) -> Self:
        data = {name: variable.default for name, variable in cls._variables.items()}
        row = {'f_key': f_key, 'name': cls._name, 'cfg': json.dumps(data)}
        if p_key:
            row['p_key'] = p_key

        p_key = await db.insert(cls._table_name, row=row)
        return cls(data=data, p_key=p_key, f_key=f_key)

    @classmethod
    async def get_or_create(cls, p_key: int, f_key: int = None) -> Self:
        record = await db.select_one(cls._table_name, {'p_key': p_key, 'name': cls._name})
        if record:
            return cls(data=json.loads(record['cfg']), p_key=p_key, f_key=f_key)
        return await cls.create(p_key, f_key)

    @classmethod
    async def get_foreign(cls, f_key: int) -> dict[int, Self]:
        """ Get all self Configs for f_key """
        records = await db.select(cls._table_name, {'f_key': f_key, 'name': cls._name})
        return {
            record['p_key']: cls(data=json.loads(record['cfg']), p_key=record['p_key'], f_key=f_key)
            for record in records
        }

    def validate(self, guild: Guild, data: dict) -> dict[str, str]:
        """ Validate each variable in the data dict, return errors """
        errors = {}
        for name, value in data.items():
            try:
                self._variables[name].validate(guild, value)
            except ValueError as e:
                errors[name] = str(e)
            except KeyError:
                errors[name] = f'Variable "{name}" does not exist.'
        return errors

    async def update(self, data: dict):
        """ Update self with partial or full data """
        full_data = {key: self.__getattribute__(key) for key in self._variables.keys()}
        full_data.update(data)

        await db.update(table=self._table_name, data={'cfg': json.dumps(full_data)}, where={'p_key': self._p_key})
        for name, value in data.items():
            self.__setattr__(name, value)

    async def reset(self):
        data = {name: variable.default for name, variable in self._variables.items()}
        await db.update(table=self._table_name, data={'cfg': json.dumps(data)}, where={'p_key': self._p_key})
        for name, value in data.items():
            self.__setattr__(name, value)

    async def delete(self):
        await db.delete(table=self._table_name, q={'p_key': self._p_key})
