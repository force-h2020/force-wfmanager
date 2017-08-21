Introduction
------------

Force Workflow Manager implements a graphical user interface to drive the
creation of workflows for the Business Decision System part of the FORCE project.
The UI is responsible for creating a workflow file that is then submitted for execution
by a command line interface utility, ``force_bdss``.

The UI presents a tree view where the workflow is created. The user must specify

- The Multi Criteria Optimizer to use, and the parameter types it
  should handle for our investigation.
- the Data Sources to use during the evaluation. Data Sources are entities responsible for
  extracting, computing or generating specific values specific to our computational investigation.
- The Key Performance Indicator calculators, additional evaluators that take the data
  produced by the DataSource and the MCO parameters, and produce the Key Performance Indicators that
  drive the MCO optimization process.

To define each of the above entities, right click on the appropriate entries in the tree.
A dialog will open, providing the available entities that can be added, together with entity specific
configuration parameters.

Once defined the workflow, it can be saved for later execution (via "Save..."), or executed
(by using "Run workflow..."). A previously saved workflow can be reloaded using "Load...".

During the execution of the ``force_bdss``, the results are displayed in the
table located in the main pane of the GUI. Those results are also displayed in
the plot, the user can choose what results to plot and the clicked point in
the plot is synchronised with the selected row in the table.
