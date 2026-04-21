"""Weather sensors — concrete :class:`Sensor` subclasses observing
environmental variables. ``height`` is inherited from :class:`Sensor`.
"""

from dataclasses import dataclass

from energydatamodel.bases import Sensor


@dataclass(repr=False, kw_only=True)
class TemperatureSensor(Sensor):
    pass


@dataclass(repr=False, kw_only=True)
class WindSpeedSensor(Sensor):
    pass


@dataclass(repr=False, kw_only=True)
class RadiationSensor(Sensor):
    pass


@dataclass(repr=False, kw_only=True)
class RainSensor(Sensor):
    pass


@dataclass(repr=False, kw_only=True)
class HumiditySensor(Sensor):
    pass
