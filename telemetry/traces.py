import logging

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
from opentelemetry._logs import get_logger_provider, set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor


# Function to setup logging telemetry with Azure Monitor and App Insights.
def setup_logging():
    """
    Function to set up logging telemetry with Azure Monitor using Python logging module.

    Note: Ensure that $APPLICATIONINSIGHTS_CONNECTION_STRING is set in env.

    """

    # Setting loging level for Azure Core and Monitor loggers to WARNING.
    logging.getLogger("azure.core").setLevel(logging.WARNING)
    logging.getLogger("azure.monitor").setLevel(logging.WARNING)

    # Configuring Python logging.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d |:| %(levelname)s |:| %(name)s |:| %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Setting up exporter for emitting logs to Azure Monitor.
    set_logger_provider(LoggerProvider())
    exporter = AzureMonitorLogExporter()
    get_logger_provider().add_log_record_processor(BatchLogRecordProcessor(exporter))

    # Attaching LoggingHandler to python root logger to tie things together.
    handler = LoggingHandler()
    logging.getLogger().addHandler(handler)


# Function to customize the Log Record Factory with custom attributes.
def customize_record_factory(**attributes):
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        for k, v in attributes.items():
            setattr(record, k, v)
        return record

    logging.setLogRecordFactory(record_factory)
