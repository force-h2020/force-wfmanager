def test_remove_datasource(self):
    self.wf_mv_name_registry.process_model_view.add_execution_layer(ExecutionLayer())
    self.assertEqual(len(self.wf_mv_name_registry.process_model_view.
                         execution_layer_model_views[0].model.data_sources), 0)
    execution_layer = self.wf_mv_name_registry.process_model_view.execution_layer_model_views[0]
    execution_layer.add_data_source(self.datasource_models[0])
    self.assertEqual(len(execution_layer.model.data_sources), 1)
    self.wf_mv_name_registry.process_model_view.remove_data_source(self.datasource_models[1])
    self.assertEqual(len(execution_layer.model.data_sources), 1)
    self.wf_mv_name_registry.process_model_view.remove_data_source(self.datasource_models[0])
    self.assertEqual(len(execution_layer.model.data_sources), 0)