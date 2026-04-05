from timedatamodel import TimeSeries as _BaseTimeSeries
from timedatamodel import TimeSeriesTable as _BaseTimeSeriesTable


class TimeSeries(_BaseTimeSeries):
    """EnergyDataModel TimeSeries — inherits from timedatamodel.TimeSeries."""
    pass


class TimeSeriesTable(_BaseTimeSeriesTable):
    """EnergyDataModel TimeSeriesTable — inherits from timedatamodel.TimeSeriesTable."""
    pass


# Electricity time series types
class ElectricityDemand(TimeSeries):
    pass

class ElectricityConsumption(TimeSeries):
    pass

class ElectricityAreaDemand(TimeSeries):
    pass

class ElectricityAreaConsumption(TimeSeries):
    pass

class ElectricitySupply(TimeSeries):
    pass

class ElectricityProduction(TimeSeries):
    pass

class ElectricityAreaSupply(TimeSeries):
    pass

class ElectricityAreaProduction(TimeSeries):
    pass

class HeatingDemand(TimeSeries):
    pass

class HeatingConsumption(TimeSeries):
    pass

class HeatingAreaDemand(TimeSeries):
    pass
