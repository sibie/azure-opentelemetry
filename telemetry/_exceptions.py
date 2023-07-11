class MetricConfigurationException(Exception):
    """
    Exception indicating that metric configuration failed due to errors in input dict. """
    pass


class MetricNotFound(Exception):
    """ Exception indicating that the input metric was not found in MetricsManager object. """
    pass
