"""
Copyright 2020-2021 The KArgParse Project, All Rights Reserved.

This software, having been partly or wholly developed and/or
sponsored by KoreLogic, Inc., is hereby released under the terms
and conditions set forth in the project's "README.LICENSE" file.
For a list of all contributors and sponsors, please refer to the
project's "README.CREDITS" file.
"""

# The second line of argparse imports are strictly here so that the
# coder can access them through this module for a custom use.
from argparse import ArgumentError, ArgumentTypeError, ArgumentParser, Namespace, __version__ as argparse_version_string, SUPPRESS, _UNRECOGNIZED_ARGS_ATTR
from argparse import Action, ArgumentDefaultsHelpFormatter, FileType, HelpFormatter, MetavarTypeHelpFormatter, RawDescriptionHelpFormatter, RawTextHelpFormatter # pylint: disable=W0611
from inspect import signature
from re import match
from sys import argv, stderr

from kargparse.formatter import KHelpFormatter
from kargparse.error import KArgumentError, KProgramError, KUsageError

class KArgumentParser(ArgumentParser):
    """
    Object that extends argparse's ArgumentParser.

    KArgumentParser parses command line strings into Python objects. This
    class is the main entry point for KArgParse. The add_argument()
    method is used to populate the parser with actions for positional and
    optional arguments. Then the parse_args() method is invoked to convert
    the arguments at the command line into an object with attributes. See
    the argparse documentation for a detailed explanation of everything
    argparse can do (https://docs.python.org/3/library/argparse.html).

    Arguments:
        prog (string, optional):
            The name of the program (default: sys.argv[0]).
        usage (string, optional):
            A usage statement for the program (default: Auto-generated
            from the arguments).
        description (string, optional):
            Text preceding the usage and help statements (default: None).
        epilog (string, optional):
            Text following the usage and help statements (default: None).
        parents (string, optional):
            Parsers whose arguments should be copied into this one
            (default: []).
        formatter_class (class, optional):
            The class for formatting the help messages. Using the original
            argparse formatters will work but some functionality will
            be reduced (default: KHelpFormatter).
        prefix_chars (string, optional):
            Characters that prefix optional arguments (default: "-").
        fromfile_prefix_chars (string, optional):
            Characters that prefix files containing additional arguments
            (default: None).
        argument_default (type, optional):
            The default value for all arguments (default: None).
        conflict_handler (string, optional):
            String indicating how to handle conflicts (default: "error").
        add_help (boolean, optional):
            Add a -h|--help option to the help statement (default: True).
        allow_abbrev (boolean, optional):
            Allow long options to be abbreviated unambiguously (default:
            True).
        add_version (string, optional):
            Add a -v|--version option to the help statement (default:
            None).
        choices_limit (integer, optional):
            Limit for the number of argument choices displayed in the
            help statement (default: 25).
        delimeter (string, optional):
            A character that delimits optional arguments in the help
            statement (default: "|").
        exit_on_error (boolean, optional):
            Exit and print the help statement if there is an
            error. Otherwise, raise an error for the user to handle. See
            the error() method for additional help (default: True).
        line_width (integer, optional):
            The line width for the usage and help statements (default:
            80).
    """

    def __init__(self,
                 prog=None,
                 usage=None,
                 description=None,
                 epilog=None,
                 parents=None,
                 formatter_class=KHelpFormatter,
                 prefix_chars="-",
                 fromfile_prefix_chars=None,
                 argument_default=None,
                 conflict_handler="error",
                 add_help=True,
                 allow_abbrev=True,
                 add_version=None,
                 choices_limit=25,
                 delimeter="|",
                 exit_on_error=True,
                 line_width=80):

        if parents is None:
            parents = []

        super().__init__(prog=prog,
                         usage=usage,
                         description=description,
                         epilog=epilog,
                         parents=parents,
                         formatter_class=formatter_class,
                         prefix_chars=prefix_chars,
                         fromfile_prefix_chars=fromfile_prefix_chars,
                         argument_default=argument_default,
                         conflict_handler=conflict_handler,
                         add_help=False, # Overridden intentionally, see self.add_help below.
                         allow_abbrev=allow_abbrev)

        # This is overriding what the parent class ArgumentParser set the
        # attribute add_help to. This is done on purpose so the -h|--help
        # argument can be added manually. Without this, the formatting of
        # the help statement for this argument would not match its peers.
        self.add_help = add_help

        self._add_version = add_version
        self._choices_limit = choices_limit
        self._delimeter = delimeter
        self._exit_on_error = exit_on_error
        self._line_width = line_width

        self._error_message = None
        self._supported_version_string = "1.1"
        self._supported_version_number = float(self._supported_version_string)

        # This variable needs to be defined before any methods are called.
        # This is the default dictionary for checking an argument's type.
        # The structure of this dictionary is: {"The keys are specified in the order: object.__name__ then repr(type(object))" : "strings that represent the type for the help statement."}
        self._allowed_types = {"int" : "integer", "str" : "string"}

        # This variable needs to be defined before any methods are called.
        # This is the default dictionary for handling error codes.
        # The structure of this dictionary is: {"The type of error." : "The exit code"}
        self._error_codes = {"argument" : 2, "program" : 70, "usage" : 1}

        # This variable needs to be defined before any methods are called.
        # This is the dictionary for handling error classes.
        # The structure of this dictionary is: {"The type of error." : "The exception class"}
        self._error_classes = {"argument" : KArgumentError, "program" : KProgramError, "usage" : KUsageError}

        # This variable needs to be defined before any methods are called.
        # This is the dictionary for handling error messages.
        # The structure of this dictionary is: {"A regular expression to match the original error message." : {"message" : "The new formatted message.", "error_type" : "The type of error."}}
        self._error_messages = {
            "^Argument (.+): conflicting option string(s?): (.+)$" : {"message" : "Argument {group[0]}: Conflicting option string{group[1]}: {group[2]}", "error_type" : "program"},
            "^Argument (.+): expected (.+) argument(s?)$" : {"message" : "Argument {group[0]}: Expected {group[1]} argument{group[2]}.", "error_type" : "usage"},
            "^Argument (.+): can't open (.+): (\\[Errno [0-9]{1,3}\\] .+)$" : {"message" : "Argument {group[0]}: Can't open {group[1]}: OSError: {group[2]}", "error_type" : "argument"},
            "^Argument (.+): Choices only supports the passing of zero or one argument.$" : {"message" : "{string}", "error_type" : "program"},
            "^Argument (.+): Invalid choice: (.+) \\(value not in choices\\)$" : {"message" : "{string}", "error_type" : "argument"},
            "^Argument (.+): Invalid choice: (.+) \\(choose from (.+)\\)$" : {"message" : "{string}", "error_type" : "argument"},
            "^Argument (.+): Invalid value: (.+)$" : {"message" : "{string}", "error_type" : "argument"},
            "^Argument (.+): The specified type '(.+)' is not supported.$" : {"message" : "{string}", "error_type" : "program"},
            "^Argument (.+): (.+) is not callable.$" : {"message" : "Argument {group[0]}: {group[1]} is not callable.", "error_type" : "program"},
            "^Argument (.+): ignored explicit argument (.+)$" : {"message" : "Argument {group[0]}: Ignored explicit argument {group[1]}", "error_type" : "usage"},
            "^Argument (.+): not allowed with argument (.+)$" : {"message" : "Argument {group[0]}: Not allowed with argument {group[1]}", "error_type" : "usage"},
            "^Argument (.+): unknown parser '(.+)' \\(choices: (.+)\\)$" : {"message" : "Argument {group[0]}: Unknown parser '{group[1]}' (choices: {group[2]})", "error_type" : "program"},
            "^ambiguous option: (.+) could match (.+)$" : {"message" : "Ambiguous option: {group[0]} could match {group[1]}", "error_type" : "usage"},
            "^cannot have multiple subparser arguments$" : {"message" : "Cannot have multiple subparser arguments.", "error_type" : "program"},
            "^one of the arguments (.+) is required$" : {"message" : "One of the arguments {group[0]} is required.", "error_type" : "usage"},
            "^the following arguments are required: (.+)$" : {"message" : "The following arguments are required: {group[0]}", "error_type" : "usage"},
            "^unrecognized arguments: (.+)$" : {"message" : "Unrecognized arguments: {group[0]}", "error_type" : "usage"},
            "^unexpected option string: (.+)$" : {"message" : "Unexpected option string: {group[0]}", "error_type" : "usage"},
            "^\\[Errno [0-9]{1,3}\\] (.+): (.+)$" : {"message" : "OSError: {string}", "error_type" : "argument"}
        }

        # Check the version of argparse to make sure it is supported.
        try:
            float(argparse_version_string)
        except ValueError:
            raise ValueError("Unsupported argparse version ({}). Float conversion failed. This should not happen unless the version number/format changed.".format(argparse_version_string)) from None
        else:
            if float(argparse_version_string) != self._supported_version_number:
                raise ValueError("Unsupported argparse version ({}). The only supported version is {}.".format(argparse_version_string, self._supported_version_string))

        # Check the exit_on_error.
        if not isinstance(self._exit_on_error, bool):
            raise TypeError("A boolean is the only allowed type value for exit_on_error.")

        # Check the choices_limit.
        if not isinstance(self._choices_limit, int):
            raise TypeError("A integer is the only allowed type value for choices_limit.")
        if self._choices_limit not in range(1001):
            raise ValueError("The choices_limit must be in the set [0, 1000].")

        # Check the line_width.
        if not isinstance(self._line_width, int):
            raise TypeError("A integer is the only allowed type value for line_width.")
        if self._line_width not in range(20, 241):
            raise ValueError("The line_width must be in the set [20, 240].")

        # Add the help argument if necessary.
        if self.add_help:
            prefix = self.prefix_chars[0]
            self.add_argument(prefix+"h", prefix*2+"help", action="help", default=SUPPRESS, help="Show this help message and exit.")

        # Add the version argument if necessary.
        if self._add_version is not None:
            if not isinstance(self._add_version, str):
                raise TypeError("A string is the only allowed type value for add_version.")
            prefix = self.prefix_chars[0]
            self.add_argument(prefix+"v", prefix*2+"version", action="version", version="{} {}".format(self.prog, self._add_version), default=SUPPRESS, help="Show the version and exit.")

    def _check_value(self, action, value):
        """
        Check the value of an argument.

        Check the value of an argument from the command line with the
        choices attribute for that argument. If the number of choices
        for an argument is greater than the choices_limit, a message
        will be displayed instead of the choices.

        Arguments:
            action (class, required):
                The argument which contains the choices and pairs with
                the value.
            value (type, required):
                The argument's converted value from the command line.

        Raises:
            ArgumentError:
                If the value is not in the choices or if choices is a
                function call and cannot be evaluated.
        """

        # If specified, the converted value must be one of the choices.
        message = ""
        if action.choices is not None:
            default = "Invalid choice: {} (value not in choices)".format(value)

            # If action.choices is callable, call it and check the return value.
            if callable(action.choices):
                # Create a signature of the callable so we can check the parameters.
                sig = signature(action.choices)
                # If no parameters, the return value should be iterable.
                if not sig.parameters:
                    if value not in action.choices():
                        message = default
                # If one parameter, the return value should be a boolean.
                elif len(sig.parameters) == 1:
                    if not action.choices(value):
                        message = default
                # Anything other than zero or one parameter is not supported.
                else:
                    message = "Choices only supports the passing of zero or one argument."
            # Otherwise, action.choices should be iterable.
            else:
                if value not in action.choices:
                    if len(action.choices) < self._choices_limit:
                        message = "Invalid choice: {} (choose from {})".format(value, ", ".join(map(repr, action.choices)))
                    else:
                        message = default

        # If message was set, we have an error.
        if message:
            raise ArgumentError(action, message)

    def _get_formatter(self):
        """Returns an intialized formatter class object."""

        # Check the formatter_class.
        if self.formatter_class == KHelpFormatter:
            return self.formatter_class(prog=self.prog,
                                        allowed_types=self._allowed_types,
                                        width=self._line_width,
                                        delimeter=self._delimeter,
                                        prefix_chars=self.prefix_chars)

        return self.formatter_class(prog=self.prog)

    def _get_value(self, action, arg_string):
        """
        Convert the value of an argument.

        Convert the value of an argument from the command line with the
        type attribute for that argument. The value will be a string
        and it will be cast into the type it's supposed to be.

        Arguments:
            action (class, required):
                The argument which contains the type and pairs with
                the arg_string.
            arg_string (string, required):
                The argument's value from the command line.

        Returns:
            value:
                The value casted into the correct type.

        Raises:
            ArgumentError:
                If the type is not callable or if there are any errors
                during the casting of the value.
        """

        # Raise an error if the action type is not callable.
        type_func = self._registry_get("type", action.type, action.type)
        if not callable(type_func):
            message = "{} is not callable.".format(type_func)
            raise ArgumentError(action, message)

        # Convert the value into the appropriate type.
        try:
            result = type_func(arg_string)
        # Raise an error if the type is not converted properly.
        except ArgumentTypeError as error:
            raise ArgumentError(action, error)
        # Raise an error if the type is not converted properly.
        except Exception as error:
            message = "Invalid value: {}".format(arg_string)
            raise ArgumentError(action, message)

        # Return the converted value.
        return result

    def add_argument(self, *args, **kwargs):
        """
        Add an argument to the parser.

        The parameters of an argument define the rules for how it
        should be parsed and handled from the command line. An extra
        restriction has been added to check the type of an argument with
        the allowed_types dictionary. See the argparse documentation
        for a detailed explanation of everything argparse can do
        (https://docs.python.org/3/library/argparse.html).

        Arguments:
            *name or *flags (string, required):
                Either a name or a list of option strings, e.g. foo or -f,
                --foo. This determines whether the argument is positional
                or optional.
            **action (string, optional):
                The basic type of action to be taken when this argument is
                encountered at the command line (default: "store_action").
            **choices (container or function, optional):
                A container of the allowable values for the argument. An
                evaluated or unevaluated function can also be passed to
                choices. If the function is evaluated, it must produce
                a container. If the function is unevaluated, it either
                takes no arguments and returns a container; or it takes
                one argument which is the value of the argument from
                the command line and returns a boolean (default: None).
            **const (type, optional):
                A constant value required by some action and nargs
                selections (default: None).
            **default (type, optional):
                The value produced if the argument is absent from the
                command line (default: None).
            **dest (string, optional):
                The name of the attribute to be added to the object
                returned by the method parse_args() (default: The name
                or the first double prefixed option).
            **help (string, optional):
                A brief description of what the argument does. The help
                supports the use of named placeholders, e.g. %(default)s,
                %(choices)s.
            **metavar (string, optional):
                A name for the argument in the help statement. This is useful
                for showing the structured input (default: None)
            **nargs (string or integer, optional):
                The number of command line arguments that should
                be consumed. This can either be an integer or a
                metacharacter, e.g. "?", "+", or "*".
            **required (boolean, optional):
                Whether or not the command line option may be omitted
                (optionals only) (default: False).
            **type (type or function, optional):
                The type to which the command line argument should be
                converted. An unevaluated function that only takes the
                value of its respective argument from the command line
                can also be passed to type. The function must convert
                and return the value of the argument into the desired
                type. The type must also be added to the allowed_types
                dictionary for this to work. See the modify_allowed_types
                for additional help (default: str).

        Returns:
            action class:
                The generated action class for this argument. The class
                is determined by the action argument.

        Raises:
            ArgumentError:
                If the argument's type is not supported or there is an
                error during the creation of the action class.
        """

        # Attempt to add the argument and exit if there are any errors.
        try:
            action = super().add_argument(*args, **kwargs)
            # Check the type to make sure it is in allowed_types.
            if action.type is not None:
                name = getattr(action.type, "__name__", repr(action.type))
                if not self._allowed_types.get(name):
                    message = "The specified type '{}' is not supported.".format(name)
                    raise ArgumentError(action, message)
        # If an ArgumentError was raised, handle the error.
        except ArgumentError as error:
            error = str(error)
            # Capitialize the first letter of the error message.
            error = error[0].upper() + error[1:]
            # Pass the error onwards to continue the error handling.
            self.error(error)

        # Return the added argument.
        return action

    def add_argument_group(self, *args, **kwargs):
        """
        Add an argument group to the parser.

        When there is a better conceptual grouping of arguments than the
        defaults, appropriate groups can be created using this method. An
        argument group object is returned containing an add_argument()
        method, the same as KArgumentParser's add_argument() method. When
        an argument is added to the group, the parser treats it just
        like a normal argument, but displays the argument in its specific
        group for the help statement.

        Arguments:
            *|**title (string, optional):
                A title for the argument group (default: None).
            *|**description (string, optional):
                A description of the argument group (default: None).
            **prefix_chars (string, optional):
                Characters that prefix optional arguments (default:
                Same as parser).
            **argument_default (type, optional):
                The default value for all arguments (default: Same
                as parser).
            **conflict_handler (string, optional):
                String indicating how to handle conflicts (default:
                Same as parser).

        Returns:
            argument group:
                An argument group object to then add arguments to.
        """

        # Check the formatter_class.
        if self.formatter_class == KHelpFormatter:
            # Do not edit the **kwargs dictionary. The **kwargs dictionary
            # is used on an argument group object that has already been
            # created. The *args tuple is used when an argument group
            # object is about to be created. This is only true for what
            # goes on inside argparse.
            if args:
                # Unpack the *args tuple, and create a mutable list.
                args = [*args]

                # Replace the argument group's title if need be.
                if args[0] == "positional arguments":
                    args[0] = "Positional Arguments"
                if args[0] == "optional arguments":
                    args[0] = "Additional Required Arguments and/or Options"

        # Return the argument group object.
        return super().add_argument_group(*args, **kwargs)

    def error(self, message):
        """
        Handles errors during the processing of arguments.

        This method is called to handle errors during the processing of
        arguments. This method is not supposed to handle programming
        errors, they should be raised directly. However, there are a
        few argparse errors that have been determined to be programming
        errors and therefore must be handled. This method will either
        call the exit() method, or raise an exception depending
        on the value of exit_on_error. If an exception is raised,
        KArgumentError and KUsageError should be the only errors
        caught. KProgramError represents a programming error and needs
        to be let through. Each exception has a user definable exit code,
        see the modify_error_codes() method for addtitonal help.

        Arguments:
            message (string, required):
                The string representation of an error.

        Raises:
            KArgumentError:
                A error during the processing of an argument. For more
                information do a help on this error.
            KProgramError:
                A programming error, this will always be raised. For
                more information do a help on this error.
            KUsageError:
                A incorrectly written command line. For more information
                do a help on this error.
        """

        # Make sure a message was provided.
        if message:
            # Look for the error in error_messages and handle the error.
            for regex, dictionary in self._error_messages.items():
                # If a match was found, handle the error.
                if match(regex, message):
                    # Format the new message.
                    message = dictionary["message"].format(group=match(regex, message).groups(), string=match(regex, message).string)
                    # Get the exit status.
                    status = self._error_codes[dictionary["error_type"]]
                    # Get the exception class.
                    exception = self._error_classes[dictionary["error_type"]]

                    # If exit_on_error is True and the error_type is not a programming error, exit the program.
                    if self._exit_on_error and dictionary["error_type"] != "program":
                        self.exit(status, message)

                    # Otherwise, raise the exception for the user to handle.
                    raise exception(message, status)

        # Raise an exception if there was not a message or a match.
        message = "Undefined error message. That should not happen. Message: {}".format(str(message))
        status = self._error_codes["program"]
        exception = self._error_classes["program"]
        raise exception(message, status)

    def exit(self, status=0, message=None):
        """
        This method terminates the program.

        This method is called when the program wants to exit. If
        exit_on_error is False, the script will only exit if the -h|--help
        or the -v|--version option is specified. If exit_on_error is
        True and the exit status is not zero, the usage statement will
        be printed.

        Arguments:
            status (integer, optional):
                The exit code for the program.
            message (string, optional):
                The string representation of an error.
        """

        # If the exit status is not zero, print the usage statement.
        if status != 0:
            # Save the error message to be used later.
            self._error_message = message
            self.print_usage(stderr)

            # Check the formatter_class.
            if self._error_message and self.formatter_class != KHelpFormatter:
                # The formatter_class is not KHelpFormatter, print the error message manually.
                self._error_message = self.prog + ": Error: " + self._error_message
                print(self._error_message, file=stderr)

        # Exit with the specified status.
        exit(status)

    def format_help(self):
        """
        Formats the help statement.

        Each section that will be part of the help statement is given
        to the formatter class to be formatted and joined together.

        Returns:
            string:
                The formatted help statement.
        """

        # Check the formatter_class.
        if self.formatter_class == KHelpFormatter:
            # Get the formatter.
            formatter = self._get_formatter()

            # Format and add the usage.
            formatter.add_usage(self.usage, self._actions, self._mutually_exclusive_groups)

            # Format and add the description.
            formatter.start_section("Description")
            formatter.add_text(self.description)
            formatter.end_section()

            # Format the positionals, optionals and user-defined groups.
            for action_group in self._action_groups:
                if action_group.title == self._optionals.title:
                    action_group._group_actions.sort(key=formatter.get_format_option_strings())

                formatter.start_section(action_group.title)
                formatter.add_text(action_group.description)
                formatter.add_arguments(action_group._group_actions)
                formatter.end_section()

            # Format and add the epilog.
            formatter.start_section("Epilog")
            formatter.add_text(self.epilog)
            formatter.end_section()

            # Format and add the error diagnostics.
            if self.add_help:
                formatter.start_section("Error Diagnostics (use -h|--help for usage details)")
            else:
                formatter.start_section("Error Diagnostics")
            formatter.add_text(self._error_message)
            formatter.end_section()

            # Determine and return the help statement from everything added above.
            return formatter.format_help()

        return super().format_help()

    def format_usage(self):
        """
        Formats the usage statement.

        Each section that will be part of the usage statement is given
        to the formatter class to be formatted and joined together.

        Returns:
            string:
                The formatted usage statement.
        """

        # Check the formatter_class.
        if self.formatter_class == KHelpFormatter:
            # Get the formatter.
            formatter = self._get_formatter()

            # Format and add the usage.
            formatter.add_usage(self.usage, self._actions, self._mutually_exclusive_groups)

            # Format and add the error diagnostics.
            if self.add_help:
                formatter.start_section("Error Diagnostics (use -h|--help for usage details)")
            else:
                formatter.start_section("Error Diagnostics")
            formatter.add_text(self._error_message)
            formatter.end_section()

            # Determine and return the usage statement from everything added above.
            return formatter.format_help()

        return super().format_usage()

    def get_allowed_types(self):
        """Returns the allowed_types dictionary."""
        return self._allowed_types

    def get_error_codes(self):
        """Returns the error_codes dictionary."""

        return self._error_codes

    def modify_allowed_types(self, **kwargs):
        """
        Modify the allowed_types dictionary.

        There are four operations that can be preformed: set, add,
        replace, and delete. Only one operation can be preformed per
        method call. If multiple operations are specified, only the
        first operation will be preformed. If the user modifies the
        allowed_types dictionary for a parser, it will only pertain to
        that parser. Each parser has to have their own allowed_types
        specified.

        Arguments:
            **set (dictionary, optional):
                Set the allowed_types dictionary. The keys are specified
                in the order: object.__name__ then repr(type(object)). The
                values are strings that represent the type for the
                help statement.
            **add (dictionary, optional):
                Add types to the allowed_types dictionary. The keys
                are specified in the order: object.__name__ then
                repr(type(object)). The values are strings that represent
                the type for the help statement. The key, value pair
                will only be added if the key is not in the dictionary.
            **replace (dictionary, optional):
                Replace types in the allowed_types dictionary. The
                keys are specified in the order: object.__name__ then
                repr(type(object)). The values are strings that represent
                the type for the help statement. The key, value pair
                will only be replaced if the key is in the dictionary.
            **delete (list, optional):
                Delete types in the allowed_types dictionary. The list
                should contain keys to remove from the dictionary.
        """

        if "set" in kwargs:
            self._allowed_types = dict(kwargs.pop("set"))
        elif "add" in kwargs:
            for key, value in dict(kwargs.pop("add")).items():
                if not self._allowed_types.get(key):
                    self._allowed_types[key] = value
        elif "replace" in kwargs:
            for key, value in dict(kwargs.pop("replace")).items():
                if self._allowed_types.get(key):
                    self._allowed_types[key] = value
        elif "delete" in kwargs:
            for key in list(kwargs.pop("delete")):
                if self._allowed_types.get(key):
                    self._allowed_types.pop(key)

    def modify_error_codes(self, **kwargs):
        """
        Modify the error_codes dictionary.

        There are three error codes that can be specified: argument,
        program, and usage. The user can specify one, two, or all three
        error codes. If the user modifies the error_codes dictionary
        for a parser, it will only pertain to that parser. Each parser
        has to have their own error_codes specified.

        Arguments:
            **argument (integer, optional):
                Set the error code for a KArgumentError.
            **program (integer, optional):
                Set the error code for a KProgramError.
            **usage (integer, optional):
                Set the error code for a KUsageError.
        """

        if "argument" in kwargs:
            self._error_codes["argument"] = int(kwargs.pop("argument"))
        if "program" in kwargs:
            self._error_codes["program"] = int(kwargs.pop("program"))
        if "usage" in kwargs:
            self._error_codes["usage"] = int(kwargs.pop("usage"))

    def parse_known_args(self, args=None, namespace=None):
        """
        Parses the known command line arguments.

        The method parse_args() calls this method to do the argument
        parsing. The only difference is an error will be produced if
        there are unknown arguments. This method will not produce an
        error if there are unknown arguments. This allows the remaining
        arguments to be passed on to another script or program.

        Arguments:
            args (list, required):
                A list of arguments to parse (default: The command
                line arguments).
            namespace(class, optional):
                The namespace is an object that attributes can be assigned
                to. Any class can be passed in or the Namespace class
                can be imported and used. If a namespace is passed is
                must already be initalized (default: A new Namespace
                object will be created).

        Returns:
            tuple:
                A two item tuple containing the populated namespace and
                the list of remaining argument strings.

        Raises:
            ArgumentError:
                If there are any errors during the parsing and processing
                of the arguments.
        """

        # If no arguments are given, default to the system arguments.
        if args is None:
            args = argv[1:]
        # Otherwise, make sure the arguments are mutable.
        else:
            args = list(args)

        # If no Namespace was given, create the default Namespace.
        # The Namespace will be built up with the parser's defaults.
        if namespace is None:
            namespace = Namespace()

        # Add any action defaults to the Namespace that aren't present.
        for action in self._actions:
            if action.dest is not SUPPRESS:
                if not hasattr(namespace, action.dest):
                    if action.default is not SUPPRESS:
                        setattr(namespace, action.dest, action.default)

        # Add any parser defaults to the Namespace that aren't present.
        for dest in self._defaults:
            if not hasattr(namespace, dest):
                setattr(namespace, dest, self._defaults[dest])

        # Attempt to parse the arguments and exit if there are any errors.
        try:
            namespace, args = self._parse_known_args(args, namespace)
            if hasattr(namespace, _UNRECOGNIZED_ARGS_ATTR):
                args.extend(getattr(namespace, _UNRECOGNIZED_ARGS_ATTR))
                delattr(namespace, _UNRECOGNIZED_ARGS_ATTR)
            return namespace, args
        # If an ArgumentError was raised, handle the error.
        # All ArgumentError's that are raised come through here except for three raised in add_argument().
        except ArgumentError as error:
            error = str(error)
            # Capitialize the first letter of the error message.
            error = error[0].upper() + error[1:]
            # Pass the error onwards to continue the error handling.
            self.error(error)

