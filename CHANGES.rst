Changelog
=========

Release 0.4.0
-------------

Released:

Release notes
~~~~~~~~~~~~~

Version 0.4.0 is a major update to the Force WfManager package, and includes a number of
backward incompatible changes, including:

* Major refactoring of source code file tree (no more ``central_pane``, ``left_side_pane`` modules)
* Renaming of many ``<name>ModelView`` subclasses to ``<name>View`` subclasses where appropriate
* Renaming of ``WfManagerResultsTask`` class to ``WfManagerReviewTask``

The following people contributed
code changes for this release:

* Matthew Evans
* James Johnson
* Frank Longford
* Nicola De Mitri
* Petr Kungurtsev


Features
~~~~~~~~

* Developers can contribute ``BaseDataView`` subclasses (#268, #270, #271, #276 #319, #323, #349
  , #350, #351), providing custom UI views of data returned from a MCO run
* Developers can contribute ``ContributedUI`` subclasses (#324, #327, #328),
  providing custom UI views of simplified Workflow builders
* New Stop / Pause functionality from the UI during a BDSS run (#354, #360)
* Additional metadata on ``BaseDataSourceModel`` traits allow them to be validated in
  the UI (#296)


Changes
~~~~~~~~

* Updated UI display of verification checks (#273)
* Rearranged source code file tree to represent 'setup' and 'review' task functionality
  (#260, #279, #287, #304)
* TreeEditor view refactored (#285, #298, #299, #304, #313, #325) to better guide user through
  Build Workflow ---> Run MCO ---> View Results process
* Replacement of many ``ModelView`` traits subclasses with ``HasTraits`` (#302)
* Individual MCOParameter and KPI views now combined into a shared notebook style view
  (#304, #313)
* ZMQ serialisation / deserialization of ``BaseDriverEvent`` objects ported to ``force_bdss``
  (#334, #339, #340, #342, #345)
* Replaced (now obsolete) ``Unicode`` traits in favour of ``Str`` (#348)


Fixes
~~~~~

* Plot refreshing issue with live data fixed (#270, #319, #323) by introducing a Pyface CallbackTimer
* Setup fixes for Windows build (#277)
* Workflow file name reader now OS independent (#283)
* Fixes to comply with Flake8 3.7.7 (#286)
* Updated TraitsUI to include TabularEditor fixes (#288)
* Startup issues with broken application memento file fixed (#290, #293, #314)
* Removed any usages of deprecated HasTraits.set_method (#294)
* Occurrences of trait assignment before super HasTraits class __init__ called removed (#313)
* References to ``BaseFactory.plugin`` attribute removed (#331, #332), whilst name and id attributes
  retained for error reporting
* References to ``Workflow.mco`` attribute updated to ``Workflow.mco_model`` (#336)
* Fix introduced to prevent user from accidentally overwriting project file (#355)

Documentation
~~~~~~~~~~~~~

* New auto-generated Sphinx documentation (#309, #312)
* General clean up of comments amd moudle imports (#317)
* Updated README (#337, #338) including build status and links to installation instructions


Maintenance and code organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Updated traitsui to version 6.1.3-5 (#275, #288, #341, #356)
* Updated pyface to version 6.1.2-5 (#275, #288, #341, #356)
* Updated chaco to version 4.8.0-1 (#341)
* Updated qt to version 4.8.7-19 (#288)
* Updated pyzmq to version 16.0.0-7 (#288)
* EDM version updated to 2.1.0 in Travis CI (#279, #297, #335) using python 3.6
  bootstrap environment
* Better support for QT in Travis CI (#284), XVFB / libglu drivers explicitly installed
* Travis CI now runs 2 jobs: Linux Ubuntu Bionic (#284) and MacOS (#297)
* Better handling of ClickExceptions in CI (#305)

Release 0.3.0
-------------

- Upgraded python version to 3.6 (PR #252)
- Split workflow into a setup task and a results task (PR #239)
- Reorganised UI (PR #248)
- Switched to from TableEditor to TabularEditor in results pane to improve
  performance (PR #255)
- Added debug logging option

Release 0.2.0
-------------

- Changes to accommodate for the ITWM prototype.

Release 0.1.0
-------------

- Initial release. Provides a UI environment to setup and invoke a BDSS evaluation.
