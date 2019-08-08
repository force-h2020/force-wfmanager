from force_bdss.data_sources.base_data_source_factory import (
    BaseDataSourceFactory
)
from force_bdss.tests.dummy_classes.data_source import (
    DummyDataSource, DummyDataSourceModel
)


class DummyFactory(BaseDataSourceFactory):
    def get_data_source_class(self):
        return DummyDataSource

    def get_model_class(self):
        return DummyDataSourceModel

    def get_identifier(self):
        return "factory"

    def get_name(self):
        return '   Really cool factory  '
