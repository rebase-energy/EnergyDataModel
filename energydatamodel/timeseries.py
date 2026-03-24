"""
Semantic time series constructors.

Previously this module defined subclasses of the old ``edm.TimeSeries``
(e.g. ``ElectricityDemand``, ``ElectricitySupply``) that added a ``location``
or ``area`` field to a pandas-backed wrapper.

These subclasses are now **obsolete**. The same semantics are expressed
directly through :class:`timedatamodel.TimeSeriesTable` metadata:

- **location** is a first-class per-column field on ``TimeSeriesTable``
  (and on ``TimeSeries``), so there is no longer any need to subclass in
  order to carry it.

- **area** (``GeoPolygon`` / ``GeoMultiPolygon``) can be stored as a label
  or as a custom attribute on the enclosing ``EnergyAsset`` subclass.

- The **semantic distinction** between demand, supply, production, and
  consumption is expressed through :class:`timedatamodel.DataType`:

  ============================================  ==============================
  Old class                                     New approach
  ============================================  ==============================
  ``ElectricityDemand`` / ``ElectricityConsumption``  ``DataType.ACTUAL`` + label ``{"direction": "consumption"}``
  ``ElectricitySupply`` / ``ElectricityProduction``   ``DataType.ACTUAL`` + label ``{"direction": "production"}``
  ``ElectricityAreaDemand``                     same, plus ``GeoPolygon`` on the asset
  ``HeatingDemand`` / ``HeatingConsumption``    ``DataType.ACTUAL`` + label ``{"carrier": "heat", "direction": "consumption"}``
  ``ElectricityPrice``                          ``DataType.REFERENCE`` + label ``{"carrier": "electricity"}``
  ``CarbonIntensity``                           ``DataType.REFERENCE`` + label ``{"signal": "carbon_intensity"}``
  ============================================  ==============================

Example — electricity production at a point location::

    import timedatamodel as tdm

    ts = tdm.TimeSeries.from_pandas(
        df,                               # pandas DataFrame with valid_time index
        name="production",
        unit="kWh",
        data_type=tdm.DataType.ACTUAL,
        frequency=tdm.Frequency.PT1H,
        location=tdm.GeoLocation(longitude=14.97, latitude=63.54),
        labels={"carrier": "electricity", "direction": "production"},
    )

Example — building a multi-signal ``TimeSeriesTable`` for a wind turbine::

    table = tdm.TimeSeriesTable.from_timeseries(
        [ts_active_power, ts_wind_speed, ts_iec_state],
        frequency=tdm.Frequency.PT1H,
    )
    turbine.timeseries = table
"""

# No classes are defined here. See timedatamodel.TimeSeries,
# timedatamodel.TimeSeriesTable, and timedatamodel.DataType.
