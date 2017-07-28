Workflow manager concept 
========================

As part of task 3.4 we need to develop a workflow manager.  The program must be
similar to modeFRONTIER, in the sense that not only it makes possible to
construct and execute the workflow (costructed from a set of data sources, execution engines,
and Key Property Indicators (KPI) extractors), but also to collect the resulting data and perform
analysis.

Overall requirements:

    1. Ability to compose a workflow "connecting icons" and store it as part of the project.
       For simplicity, only one workflow per project is allowed.
    2. Ability to run the workflow in a queued scheduler, so that the application 
       does not need to run to retrieve the result
    3. The executing workflow must dump to a python file which actually performs the
       execution. We do not expect reading back this file to be feasible to 
       reconstruct the workflow graphically, so we need a more reliable representation
       for stored workflows.
    4. once the evaluation is over, the KPI are collected and showed as a spreadsheet 
       and as a plot.


Main window
-----------

Opening the program will open the project and thus the associated workflow. 
The main window should have multiple tabs, 

    - first tab will show and allow the configuration of the workflow
    - second tab has the execution environment, the outputs, the progress and 
      the setup of the MCO.
    - third tab has data visualization.


Workflow configuration
----------------------

The tab content will be split into two parts:

    - A palette of available engines, data sources, variables, that can be dragged and dropped on the canvas
    - A canvas where the graph from the above components is constructed.

Each individual component can be double clicked to expose its configuration options. A dialog
with the appropriate information will be shown.

Execution
---------

Once the workflow is set, the execution tab can be used. Once again, the tab content is split into two parts. The first part
is configuration for:

    - configuration option for the pipeline manager (luigi) e.g. on which machines to dispatch, how many processors, etc.
    - Multi Criteria Optimization (MCO) settings, specifically which input variables to modify, the ranges and constraints
      of each values, which parameter space exploration strategy we want (simplex/genetic algorithm) and which key indicators
      the MCO should use to evaluate the quality of the result.

Once again, the available MCO come from a palette that is plugin based. 

The second part shows the outputs of the various executions.

When everything is set, we can start the pipeline, which should keep running regardless
if the workflow manager is running or not, meaning that can operate in
"disconnected mode" and reattach at a later stage when restarted.

To manage the pipeline, we plan to use Luigi.  The workflow graph will be
rendered into a python script whose content appropriately map the graphically
expressed workflow. Luigi will drive this pipeline in the script.

It is at this stage unclear how the script can retrieve the state of the
pipeline as it progresses, but we can take advantage of Luigi web client,
maybe?

Analysis
--------

As the various runs from the MCO complete, the KPIs are extracted. The associated input data
and the KPIs are shown in the third tab, which provides both a tabular view (excel-like) and
a plot view (with chaco) of the points.


Design notes
------------

Clearly, the MCO must direct the execution and the creation of new input according to the
obtained results, so they must be in an orchestration role, rather than being part of the
workflow. In other words, the workflow is a script that runs independently, and the MCO decides 
the input to pass to it and thus executes as part of our workflow manager.

MCO, KPI evaluators, and Engines, must export information not only for the integration 
in the framework, but also to present UI elements (config dialogs, icons) to the workflow 
manager UI.

Having the MCO separated from the pipeline means that our python script with the pipeline can
run only on one set of parameters, and the MCO is external. Do we want the script to be able to do
MCO as well, thus delivering the whole KPI table once run?
