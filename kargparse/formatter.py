"""
Copyright 2020-2021 The KArgParse Project, All Rights Reserved.

This software, having been partly or wholly developed and/or
sponsored by KoreLogic, Inc., is hereby released under the terms
and conditions set forth in the project's "README.LICENSE" file.
For a list of all contributors and sponsors, please refer to the
project's "README.CREDITS" file.
"""

from argparse import HelpFormatter, ONE_OR_MORE, OPTIONAL, PARSER, REMAINDER, SUPPRESS, ZERO_OR_MORE

class KHelpFormatter(HelpFormatter):
    """
    Object that extends argparse's HelpFormatter.

    This class is an extension of HelpFormatter from the argparse
    module. This is the formatter for generating usage messages and
    argument help strings.

    Arguments:
        prog (string, required):
            The name of the program.
        indent_increment (integer, optional):
            The number of spaces each indent will be (default: 4).
        max_help_position (integer, optional):
            The maximum indentation level of an argument's help text
            (default: 24).
        width (integer, optional):
            The width all lines will be formatted to (default: 80).
        allowed_types (dictionary, optional):
            See KArgumentParser's add_argument() and
            modify_allowed_types() methods for help.
        delimeter (string, optional):
            A character that delimits optional arguments in the help
            statement (default: "|").
        prefix_chars (string, optional):
            Characters that prefix optional arguments (default: "-").
    """

    def __init__(self,
                 prog,
                 indent_increment=4,
                 max_help_position=24,
                 width=80,
                 allowed_types=None,
                 delimeter="|",
                 prefix_chars="-"):

        super().__init__(prog=prog,
                         indent_increment=indent_increment,
                         max_help_position=max_help_position,
                         width=width)

        self._allowed_types = allowed_types
        self._delimeter = delimeter
        self._prefix_chars = prefix_chars

        # Check the allowed_types.
        if not isinstance(self._allowed_types, dict):
            raise TypeError("A dictionary is the only allowed type value.")

    def _expand_help(self, action):
        """
        Format the help statement for an argument.

        This method expands the help statement for an argument. If
        the help statement contains named placeholders for any of the
        parameters that argument has, they will be replaced with the
        value of that parameter. See KArgumentParser's add_argument()
        method for help on "help".

        Arguments:
            action (class, required):
                The argument to format the help statement for.

        Returns:
            string:
                The formatted help statement.
        """

        # Remove any parameters with the name SUPPRESS.
        parameters = dict(vars(action), prog=self._prog)
        for name in list(parameters):
            if parameters[name] is SUPPRESS:
                del parameters[name]
        # If a parameter's value has the attribute "__name__", replace that value with the name.
        # This is used to help clean up the values for presentation in the help text.
        for name in list(parameters):
            if hasattr(parameters[name], "__name__"):
                parameters[name] = parameters[name].__name__
        # Get the help text.
        help_text = self._get_help_string(action)
        # Format the help text with the parameters.
        formatted_help = help_text % parameters

        # Return the formatted help.
        return formatted_help

    def _format_action(self, action):
        """
        Formats an argument for the help statement.

        This method formats an argument for the help
        statement. Depending on if the argument is positional or optional,
        it will be formatted accordingly.

        Arguments:
            action (class, required):
                The argument to be formatted.

        Returns:
            string:
                The formatted argument.
        """

        parts = []
        indent = self._current_indent
        # The endent leaves room for "  (required) " or "  (optional) " at the end
        # of the action header for optional actions.
        endent = 13

        # Build the full action header.
        action_header = self._format_action_invocation(action)
        # If there are option_strings for this action, it is an optional argument.
        if action.option_strings:
            # Wrap the action header.
            header_lines = self._split_lines(action_header, self._width - indent - endent)

            # Add a statement declaring if this action is required or optional.
            whitespace = self._width - indent - len(header_lines[0]) - endent
            if action.required:
                header_lines[0] = "{}{}  (required) ".format(header_lines[0], " " * whitespace)
            else:
                header_lines[0] = "{}{}  (optional) ".format(header_lines[0], " " * whitespace)
        # Otherwise, this action is a positional argument.
        else:
            # Wrap the action header.
            header_lines = self._split_lines(action_header, self._width - indent)
        for line in header_lines:
            parts.append("{}{}\n".format(" " * indent, line))

        # If there is help for this action, format and add the help statement.
        if action.help:
            # Check the indent level with the max_help_position.
            self._indent()
            if self._current_indent > self._max_help_position:
                indent = self._max_help_position
            else:
                indent = self._current_indent

            # Get the formatted help for this action.
            formatted_help = self._expand_help(action)
            # Wrap the help statement to match what the action header was wrapped to.
            if action.option_strings:
                help_lines = self._split_lines(formatted_help, self._width - indent - endent)
            else:
                help_lines = self._split_lines(formatted_help, self._width - indent)
            for line in help_lines:
                parts.append("{}{}\n".format(" " * indent, line))
            self._dedent()
        parts.append("\n")

        # If there are any subactions for this action, recursively
        # call this method to add each formatted subaction.
        for subaction in self._iter_indented_subactions(action):
            parts.append(self._format_action(subaction))

        # Join all of the individual parts together.
        formatted_action = self._join_parts(parts)

        # Return the formatted action.
        return formatted_action

    def _format_action_input(self, action):
        """
        Formats the input for an argument.

        This method formats an argument's input for usage and help
        statements. The formatted input is based on how many times
        the argument is required. See KArgumentParser's add_argument()
        method for help on "nargs".

        Arguments:
            Arguments:
            action (class, required):
                The argument to format the input for.
        """

        formatted_input = ""
        # Get the formatted metavar for this action.
        formatted_metavar = self._format_metavar(action)
        # Build the formatted input.
        if action.nargs is None:
            # None is the default value for action.nargs.
            formatted_input = "<{0}>".format(formatted_metavar)
        elif action.nargs == OPTIONAL:
            formatted_input = "[<{0}>]".format(formatted_metavar)
        elif action.nargs == ZERO_OR_MORE:
            formatted_input = "[<{0}> [<{0}> [...]]]".format(formatted_metavar)
        elif action.nargs == ONE_OR_MORE:
            formatted_input = "<{0}> [<{0}> [...]]".format(formatted_metavar)
        elif action.nargs == REMAINDER:
            formatted_input = "..."
        elif action.nargs == PARSER:
            formatted_input = "{{{0}}} ...".format(formatted_metavar)
        else:
            # If action.nargs is an integer, create a formatted string of that many values.
            # If action.nargs is zero, formatted_input will be an empty string.
            formatted_input = (("<{0}> " * action.nargs).format(formatted_metavar)).strip()

        # Return the formatted input.
        return formatted_input

    def _format_action_invocation(self, action):
        """
        Formats the header for each argument in the help statement.

        The header for a positional argument consists of the type value
        for that argument. The header for a optional argument consists
        of the option_strings and the type value for that argument.

        Arguments:
            action (class, required):
                The argument to be formatted.

        Returns:
            string:
                The formatted argument header.
        """

        # If there are option_strings for this action, it is an optional argument.
        if action.option_strings:
            parts = []
            # Get the formatted options for this action. The default format is {-s|--long}.
            formatted_options = self._format_option_strings(action, key=False)
            parts.append(formatted_options)

            # Get the formatted input for this action.
            formatted_input = self._format_action_input(action)
            if formatted_input:
                parts.append(formatted_input)

            # Join all of the individual parts together.
            action_header = " ".join([part for part in parts if part])

        # Otherwise, this action is a positional argument.
        else:
            # Get the formatted input for this action.
            formatted_input = self._format_action_input(action)
            action_header = formatted_input

        # Return the formatted action header.
        return action_header

    def _format_actions_usage(self, actions, groups):
        """
        Formats the core of the usage statement.

        This method formulates the actions usage. The actions usage
        is the core of the usage statement. This is where all of the
        actions that will go into the usage statement are formatted and
        joined together.

        Arguments:
            actions (list, required):
                A list of the arguments to format.
            groups (list, required):
                A list of mutually exclusive groups to format.

        Returns:
            string:
                The formatted core of the usage statement.
        """

        # This is for all the actions that aren't part of a mutually exclusive group.
        trimmed_actions = []
        trimmed_actions.extend(actions)
        # This is for all of the formatted mutually exclusive groups.
        formatted_groups = []

        # Format the actions in the mutally exclusive groups and remove them from trimmed_actions.
        for group in groups:
            try:
                # Find the first mutually exclusive action of the group in the actions list.
                start = trimmed_actions.index(group._group_actions[0])
            except ValueError:
                continue
            else:
                # Calculate the last mutually exclusive action of the group in the actions list.
                end = start + len(group._group_actions)
                # Check to make sure the indexing of the actions list was correct.
                if trimmed_actions[start:end] == group._group_actions:
                    # If the indexing was correct, trim the group actions out of trimmed_actions.
                    del trimmed_actions[start:end]
                    # Format all of the group actions.
                    formatted_group = self._format_mutually_exclusive_group(group)
                    formatted_groups.append(formatted_group)
        # Sort the mutally exclusive groups.
        formatted_groups.sort()

        # Split the remaining actions in trimmed_actions into optionals or positionals.
        parts = []
        positionals = []
        optionals = []
        for action in trimmed_actions:
            # Don't include the option if action.help is SUPPRESS.
            if action.help is SUPPRESS:
                continue
            # If there are option_strings for this action, it is an optional argument.
            if action.option_strings:
                optionals.append(action)
            # Otherwise, this action is a positional argument.
            else:
                positionals.append(action)

        # Format the optional-optional actions.
        for action in optionals:
            if not action.required:
                parts.append("[options]")
                break

        if "[options]" not in parts:
            for group in groups:
                if not group.required:
                    parts.append("[options]")
                    break

        # Format the required-optional actions.
        if optionals:
            # Sort the optionals.
            optionals.sort(key=self._format_option_strings)
            for action in optionals:
                # Only format required optionals.
                if action.required:
                    # Get the formatted options for this action. The default format is {-s|--long}.
                    formatted_options = self._format_option_strings(action, key=False)
                    # Get the formatted input for this action.
                    formatted_input = self._format_action_input(action)

                    parts.append(formatted_options)
                    parts.append(formatted_input)

        # Add the formatted mutally exclusive groups here.
        for formatted_group in formatted_groups:
            parts.append(formatted_group)

        # Format the positional actions.
        if positionals:
            for action in positionals:
                # Get the formatted input for this action.
                formatted_input = self._format_action_input(action)
                parts.append(formatted_input)

        # Join all of the individual parts together.
        action_usage = " ".join([part for part in parts if part])

        # Return the action_usage.
        return action_usage

    def _format_args(self, action, default_metavar):
        """
        The method _format_action_input() replaces this method.

        There is one call to this method in _ActionsContainer's
        add_argument() method. That call is preforming a check that is
        no longer needed. The rest of the calls to this method have been
        changed to call _format_action_input().

        Arguments:
            action (class, required):
                The argument to format the input for.
            default_metavar (string, required):
                The metavar to default to.
        """

        return

    def _format_metavar(self, action):
        """
        Formats the metavar for an argument.

        This is the name for an argument in the help statement. If there
        is a metavar specified, that will be used first. If the argument
        is positional and there is no metavar, the dest will be used. If
        the argument is optional and there is no metavar, the type will
        be used next. If the argument is optional and there is no metavar
        or type, the formatted metavar will default to "value".

        Arguments:
            action (class, required):
                The argument to format the metavar for.

        Returns:
            string:
                The formatted metavar.
        """

        formatted_metavar = ""
        # Try to get any subactions for this action.
        subactions = ""
        try:
            subactions = action._get_subactions
        except AttributeError:
            pass

        # If we have any subactions, this action is a subparser.
        if subactions:
            # Recursively call this method and build a string of all the subaction's metavars.
            formatted_metavar = "|".join([self._format_metavar(subaction) for subaction in subactions()])
        # Otherwise, this is a normal action and prepare the metavar accordingly.
        elif action.metavar is None:
            # If there are option_strings for this action, it is an optional argument.
            if action.option_strings:
                # This action doesn't have a metavar or a type, so default to "value".
                if action.type is None:
                    formatted_metavar = "value"
                else:
                    name = getattr(action.type, "__name__", repr(action.type))
                    formatted_metavar = self._allowed_types[name]
            # Otherwise, this action is a positional argument.
            else:
                formatted_metavar = action.dest
        # This action has a metavar, so use that.
        else:
            formatted_metavar = action.metavar

        # Return the formatted metavar.
        return formatted_metavar

    def _format_mutually_exclusive_group(self, group):
        """
        Formats the arguments for a required mutually exclusive group.

        The mutually exclusive group is only formatted if it's
        required. Only required groups show up in the usage statment. The
        formal name for each optional argument is used along with the
        type value. The formatted mutually exclusive group will look
        like {--foo <string>|--bar <integer>}.

        Arguments:
            group (list, required):
                A list of a mutually exclusive group's optional arguments
                to format.

        Returns:
            string:
                The formatted mutually exclusive group.
        """

        formatted_group = ""
        formatted_actions = []

        # Only format the mutually exclusive group if it's required.
        if group.required:
            # Sort the actions by their option_strings, then format each action.
            for action in sorted(group._group_actions, key=self._format_option_strings):
                # Don't include the option if action.help is SUPPRESS.
                if action.help is SUPPRESS:
                    continue

                # Get the formal name for this action.
                formal_name = self._get_formal_name(action)
                # Get the formatted input for this action.
                formatted_input = self._format_action_input(action)

                # Format the formal name with the formatted input.
                if formatted_input:
                    formatted_actions.append("{} {}".format(formal_name, formatted_input))
                else:
                    formatted_actions.append(formal_name)

            # Format the mutually exclusive group.
            formatted_group = self._delimeter.join(formatted_actions)
            formatted_group = "{{{}}}".format(formatted_group)

        # Return the formatted group.
        return formatted_group

    def _format_option_strings(self, action, key=True):
        """
        Formats an optional argument's option_strings.

        When the key=True, this method concatenates an optional
        argument's option_strings in semi-alphabetical order without
        the prefixes. Case is also ignored because it will create an
        improper sort. This mode is designed to be used as the "key"
        argument in python's sort() or sorted() methods to order a
        list of optional arguments. The concatenated option_strings will
        look like "slong".

        When the key=False, this method formats an optional argument's
        option_strings in semi-alphabetical order with a delimiter. The
        short options are first, followed by the long options. This
        mode is designed to format an optional argument's option_strings
        for the help statement. The formatted option_strings will look
        like {-s|--long}.

        Arguments:
            action (class, required):
                The argument which contains the option_strings to format.

        Returns:
            string:
                The formatted option_strings.
        """

        formatted_options = []

        # Get the ordered options.
        ordered_options = self._order_option_strings(action)

        # Check if the key flag is set.
        if key:
            # Strip off any prefixes from each option and ignore case.
            ordered_options = [prefixed_option.lstrip(self._prefix_chars).lower() for prefixed_option in ordered_options]
            # Format the options.
            formatted_options = "".join(ordered_options)
        else:
            # Format the options.
            formatted_options = self._delimeter.join(ordered_options)
            formatted_options = "{{{}}}".format(formatted_options)

        # Return the formatted options.
        return formatted_options

    def _format_usage(self, usage, actions, groups, prefix):
        """
        Formats the usage statement.

        This method uses the positional and optional arguments to
        format an informative usage statement.

        Arguments:
            usage (string, required):
                The usage statement to use (default: An automatically
                generated usage statement).
            actions (list, required):
                A list of the arguments to format.
            groups (list, required):
                A list of mutually exclusive groups to format.
            prefix (string, required):
                The prefix to use (default: "Usage: ").

        Returns:
            string:
                The formatted usage statement.
        """

        if prefix is None:
            prefix = "Usage: "

        # If the usage is specified, use that.
        if usage is not None:
            # Try to format the usage with the program name.
            usage = usage % dict(prog=self._prog)
        # If no optionals or positionals are available, usage is just the program name.
        elif usage is None and not actions:
            usage = self._prog
        # If optionals and positionals are available, create the usage.
        else:
            parts = []
            indent = len(prefix)
            # Build the full usage statement.
            action_usage = self._format_actions_usage(actions, groups)
            action_usage = "{} {}".format(self._prog, action_usage)

            # Wrap the usage statement.
            # The first line of the usage is wrapped without an indent.
            usage_lines = self._split_lines(action_usage, self._width - indent)
            parts.append("{}\n".format(usage_lines[0]))
            # The first line is then removed from the usage statement.
            action_usage = action_usage[len(usage_lines[0]):]
            # The rest of the usage is wrapped with an indent.
            indent += self._indent_increment
            usage_lines = self._split_lines(action_usage, self._width - indent)
            for line in usage_lines:
                parts.append("{}{}\n".format(" " * indent, line))

            # Join all of the individual parts together.
            usage = self._join_parts(parts)

        # Add the prefix and return the usage statement.
        return "{}{}\n".format(prefix, usage)

    def _get_formal_name(self, action):
        """
        Gets the formal name of an argument with option_strings.

        The first double prefixed option is the formal name for an
        option. If there is no double prefixed option, the first single
        prefixed option is taken. If there is no single prefixed option,
        the first option is taken.

        Arguments:
            action (class, required):
                The argument which contains option_strings.

        Returns:
            string:
                The formal name.
        """

        # Get the formal name for this action.
        formal_name = ""
        for option in action.option_strings:
            if option[0] in self._prefix_chars:
                if option[1] in self._prefix_chars:
                    formal_name = option
                    break
                else:
                    if not formal_name:
                        formal_name = option
        # If a formal name was not found, take the first option_string for this action.
        if not formal_name:
            formal_name = action.option_strings[0]

        # Return the formal name.
        return formal_name

    def _order_option_strings(self, action):
        """
        Orders an optional argument's option_strings.

        This method orders an optional argument's option_strings
        semi-alphabetically based on prefix length. Case is also ignored
        because it will create an improper sort. The short options are
        first, followed by the long options. The ordered option_strings
        will look like [-s, --long].

        Arguments:
            action (class, required):
                The argument which contains the option_strings to order.

        Returns:
            list:
                The ordered option_strings.
        """

        ordered_options = []

        # Ignore case and sort the option_strings.
        sorted_prefixed_options = sorted(action.option_strings, key=str.casefold)
        # Find the length of the longest prefix.
        longest_prefix_length = len(sorted_prefixed_options[0]) - len(sorted_prefixed_options[0].lstrip(self._prefix_chars))

        # Loop through the prefix lengths in ascending order.
        for prefix_length in range(1, longest_prefix_length+1):
            for prefixed_option in sorted_prefixed_options:
                # Check if the prefix_length matches the prefixed_option's prefix_length.
                if prefix_length == len(prefixed_option) - len(prefixed_option.lstrip(self._prefix_chars)):
                    ordered_options.append(prefixed_option)

        # Return the ordered options.
        return ordered_options

    def format_help(self):
        """
        Formats the help statement.

        This is the last method called in the formatting sequence. The
        subclass _Section has a format_help() method which is called to
        do the actual formatting of the help statement. This method then
        removes the extra newlines from the returned help statement.

        Returns:
            string:
                The formatted help statement.
        """

        help_statement = self._root_section.format_help()
        if help_statement:
            help_statement = self._long_break_matcher.sub("\n\n", help_statement).strip("\n")
            # Format the help statement with the proper amount of newlines.
            if "Usage:" in help_statement or "Positional Arguments:" in help_statement or "Additional Required Arguments and/or Options:" in help_statement:
                help_statement = "\n{}\n\n".format(help_statement)
            # This format is specifically for the version action.
            else:
                help_statement = "{}\n".format(help_statement)

        # Return the formatted help statement.
        return help_statement

    def get_format_option_strings(self):
        """Returns the method _format_option_strings()."""

        return self._format_option_strings

