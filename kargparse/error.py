"""
Copyright 2020-2021 The KArgParse Project, All Rights Reserved.

This software, having been partly or wholly developed and/or
sponsored by KoreLogic, Inc., is hereby released under the terms
and conditions set forth in the project's "README.LICENSE" file.
For a list of all contributors and sponsors, please refer to the
project's "README.CREDITS" file.
"""

class KArgParseError(Exception):
    """
    The base class for custom KArgParse exceptions.

    In KArgumentParser there is an error() method that handles all of
    the error messages. If exit_on_error is False (see KArgumentParser),
    then those error messages are assigned to one of the custom exception
    classes below. That class is raised to the user for handling. The
    user should only catch KArgumentError and KUsageError. KProgramError
    represents a programming error and should be let through. Each
    exception class has the attributes: message and status. The user
    can use those attributes to print the error message and exit with
    the given status.

    Attributes:
        message (string, required):
            The error message.
        status (integer, required):
            The exit code.
    """

    def __init__(self, message, status):
        super().__init__(message, status)
        self.message = message
        self.status = status

    def __str__(self):
        """Return a printable representation of this error."""

        return self.message

class KArgumentError(KArgParseError):
    """
    This exception is for argument errors.

    If there is an error during the processing of an argument, it is
    classified as an argument error. If this error is raised, that means
    the command line met the requirements of the help statement.
    """

class KProgramError(KArgParseError):
    """
    This exception is for programming errors.

    These errors happen when the user's script is using KArgParse
    programmatically incorrect. Programming errors are not supposed to
    be caught and handled. This exception class was created to handle
    a special case in KArgumentParser's error() method.
    """

class KUsageError(KArgParseError):
    """
    This exception is for usage errors.

    If there is an error during the parsing of the command line, it is
    classified as a usage error. If this error is raised, that means
    the command line did not meet the requirements of the help statement.
    """

