#  (C) Copyright 2010-2020 Enthought, Inc., Austin, TX
#  All rights reserved.

import subprocess
from unittest import mock

from force_bdss.api import (
    Workflow, WorkflowReader, WorkflowWriter,
    InvalidFileException
)


def mock_dialog(dialog_class, result, path=''):
    def mock_dialog_call(*args, **kwargs):
        dialog = mock.Mock(spec=dialog_class)
        dialog.open = lambda: result
        dialog.path = path
        return dialog
    return mock_dialog_call


def mock_file_reader(*args, **kwargs):
    def read(*args, **kwargs):
        workflow = Workflow()
        return workflow
    reader = mock.Mock(spec=WorkflowReader)
    reader.read = read
    return reader


def mock_file_writer(*args, **kwargs):
    def write(*args, **kwargs):
        return ''
    writer = mock.Mock(spec=WorkflowWriter)
    writer.write = write
    return writer


def mock_confirm_function(result):
    def mock_conf(*args, **kwargs):
        return result
    return mock_conf


def mock_file_reader_failure(*args, **kwargs):
    def read(*args, **kwargs):
        raise InvalidFileException("OUPS")
    reader = mock.Mock(spec=WorkflowReader)
    reader.read = read
    return reader


def mock_os_remove(*args, **kwargs):
    raise OSError("OUPS")


def mock_return_args(*args, **kwargs):
    return args


def mock_return_none(*args, **kwargs):
    return


def mock_subprocess(*args, **kwargs):
    def check_call(*args, **kwargs):
        return
    mock_subprocess_module = mock.Mock(spec=subprocess)
    mock_subprocess_module.check_call = check_call
    return mock_subprocess_module
