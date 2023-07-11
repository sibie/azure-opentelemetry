from _exceptions import MetricConfigurationException, MetricNotFound
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader


class MetricsManager:
    """
    A class to interface with Azure Monitor and App Insights to export custom metrics.

        Parameters:

        name (str): The name of the instrumenting module. It is recommended not to use __name__.
        interval (str): The time interval in millis to collect and pass metrics to the exporter.
        config (dict): Config dictionary describing custom metrics to implement.
        attributes (dict): Dictionary of attributes to be passed with every metric record.

        Attributes:

        meter (Meter): Meter that is used for instrumentation with Azure.
        metrics (dict): Dictionary describing custom metrics to record measurements with.
        attributes (dict): Custom attributes to emit with each metric export.

        Methods:

        record(metric: str, amount: float):
            Record a measurement for the specified custom metric.

        add(config: dict):
            Add new metrics using input config as a reference.

        remove(metric: str):
            Remove a metric.

        add_attributes(attributes: dict):
            Add a dict of attributes into the metric manager.

        remove_attribute(attribute: str):
            Remove an attribute from the metric manager.

        Notes:

        Raises MetricConfigurationException if the data in input config was bad.

        Ensure that $APPLICATIONINSIGHTS_CONNECTION_STRING is set in env before use.

        Currently this class only supports Histogram type metrics.

        Example Config:
                        config = {
                            "<metric_key>": {
                                "name": "<metric_name>",
                                "unit": "<metric_unit>",
                                "description": "<metric_description>"
                            },
                            "latency": {
                                "name": "latency",
                                "unit": "s",
                                "description": "Request latency for API calls."
                            }
                        }

    """

    def __init__(self, name: str, interval: float, config: dict, attributes: dict):
        # Setting up Azure Exporter and Meter Provider.
        exporter = AzureMonitorMetricExporter()
        reader = PeriodicExportingMetricReader(exporter, export_interval_millis=interval)
        metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))
        self.meter = metrics.get_meter_provider().get_meter(name)

        # Creating metric aggregators in the meter based on input config.
        self.metrics = {}
        try:
            for key in config:
                self.metrics[key] = self.meter.create_histogram(
                    config[key]["name"], config[key]["unit"], config[key]["description"]
                )
        except KeyError as e:
            raise MetricConfigurationException from e

        # Custom attributes to emit with each metric export.
        self.attributes = attributes

    def record(self, metric: str, amount: float):
        """
        Record a measurement for the specified custom metric.

                Parameters:
                        metric (str): Metric identifier, i.e. unique key of the metric to use.
                        amount (float): Float measurement to export.

                Returns:
                    None or MetricNotFound Exception if the metric key was not found.

        """

        try:
            self.metrics[metric].record(amount, self.attributes)
        except KeyError as e:
            raise MetricNotFound from e

    def add(self, config: dict):
        """
        Add new metrics using input config as a reference.

                Parameters:
                        config (dict): Config dictionary describing custom metrics to implement.

                Note: If the metric already exists, it will be overwritten.

        """

        try:
            for key in config:
                self.metrics[key] = self.meter.create_histogram(
                    config[key]["name"], config[key]["unit"], config[key]["description"]
                )
        except KeyError as e:
            raise MetricConfigurationException from e

    def remove(self, metric: str):
        """
        Remove a metric. Raises MetricNotFound exception if the metric key was not found.

                Parameters:
                        attributes (dict): Dictionary of attributes to be added.

        """

        try:
            self.metrics.pop(metric)
        except KeyError as e:
            raise MetricNotFound from e

    def add_attributes(self, attributes: dict):
        """
        Add a dict of attributes into the metric manager.

                Parameters:
                        attributes (dict): Dictionary of attributes to be added.

                Note: If the attribute already exists, it will be overwritten.

        """

        for key in attributes:
            self.attributes[key] = attributes[key]

    def remove_attributes(self, attribute: str):
        """
        Remove an attribute from the metric manager.

                Parameters:
                        attribute (str): Key of the attribute to be deleted.

        """

        if attribute in self.attributes:
            self.attributes.pop(attribute)
