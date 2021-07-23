#!/usr/bin/env python3

from kargparse.parser import ArgumentError, FileType, KArgumentParser, KArgumentError, KProgramError, KUsageError, Namespace
import unittest

class TestErrors(unittest.TestCase):

    def setUp(self):
        # Create the main parser.
        self.parser = KArgumentParser(exit_on_error=False)

    def test_multiple_subparsers(self):
        # Check that a KProgramError is raised when multiple subparsers are added.
        with self.assertRaises(KProgramError) as error:
            self.parser.add_subparsers()
            self.parser.add_subparsers()
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Cannot have multiple subparser arguments.")
        self.assertEqual(error.status, 70)

    def test_unknown_parser(self):
        # Create the main parsers.
        parser_one = KArgumentParser(exit_on_error=False)
        parser_two = KArgumentParser(exit_on_error=False)
        # Create subparsers for these parsers.
        subparsers_one = parser_one.add_subparsers(dest="mode")
        subparsers_two = parser_two.add_subparsers(dest="mode")
        # Add a subparser to the subparsers.
        subparsers_one.add_parser("foo")
        subparsers_two.add_parser("bar")
        # This is not a normal case, this error is being forced.
        # Check that a ArgumentError is raised when there is an unknown parser.
        with self.assertRaises(ArgumentError) as error:
            subparsers_one(parser_one, Namespace(), [subparser for subparser in subparsers_two.choices.keys()])
        # Manually format the string.
        error = error.exception
        error = str(error)
        error = error[0].upper() + error[1:]
        # Check that a KProgramError is raised when there is an unknown parser.
        with self.assertRaises(KProgramError) as error_one:
            parser_one.error(error)
        error_one = error_one.exception
        self.assertEqual(error_one.message, "Argument mode: Unknown parser 'bar' (choices: foo)")
        self.assertEqual(error_one.status, 70)

    def test_unrecognized_arguments(self):
        # Add an argument to the parser.
        self.parser.add_argument("foo")
        # Check that a KUsageError is raised when there are unrecognized arguments.
        with self.assertRaises(KUsageError) as error:
            self.parser.parse_args(["foo", "unrecognized"])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Unrecognized arguments: unrecognized")
        self.assertEqual(error.status, 1)

    def test_unexpected_option(self):
        # Add an argument to the parser.
        self.parser.add_argument("-f", "--foo")
        # This is not a normal case, this error is being forced.
        # Check that a KUsageError is raised when there is an unexpected option.
        with self.assertRaises(KUsageError) as error:
            self.parser._get_option_tuples("++foo")
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Unexpected option string: ++foo")
        self.assertEqual(error.status, 1)

    def test_the_following_arguments_are_required(self):
        # Add an argument to the parser.
        self.parser.add_argument("foo")
        # Check that a KUsageError is raised when there are required arguments.
        with self.assertRaises(KUsageError) as error:
            self.parser.parse_args([])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "The following arguments are required: foo")
        self.assertEqual(error.status, 1)

    def test_one_of_the_arguments_is_required(self):
        # Create a mutually exclusive group.
        group = self.parser.add_mutually_exclusive_group(required=True)
        # Add arguments to the group.
        group.add_argument("-f", "--foo")
        group.add_argument("-b", "--bar")
        # Check that a KUsageError is raised when one of the arguments are required.
        with self.assertRaises(KUsageError) as error:
            self.parser.parse_args([])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "One of the arguments -f/--foo -b/--bar is required.")
        self.assertEqual(error.status, 1)

    def test_ambiguous_option(self):
        # Add arguments to the parser.
        self.parser.add_argument("-f", "--foo")
        self.parser.add_argument("-b", "--foobar")
        # Check that a KUsageError is raised when there are ambiguous arguments.
        with self.assertRaises(KUsageError) as error:
            self.parser.parse_args(["--fo"])
        # Check the error message and exit code.
        error = error.exception
        self.assertRegex(error.message, "Ambiguous option: --fo could match (?:--foo, --foobar|--foobar, --foo)")
        self.assertEqual(error.status, 1)

    def test_invalid_choice(self):
        # Create the main parser.
        parser = KArgumentParser(exit_on_error=False)
        # Add an argument to the parser.
        parser.add_argument("foo", choices=[1,2,3], type=int)
        # Check that a KArgumentError is raised when the value is not in choices.
        with self.assertRaises(KArgumentError) as error:
            parser.parse_args([0])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument foo: Invalid choice: 0 (choose from 1, 2, 3)")
        self.assertEqual(error.status, 2)

        # Create the main parser.
        parser = KArgumentParser(exit_on_error=False)
        # Add an argument to the parser.
        parser.add_argument("foo", choices=range(1,70), type=int)
        # Check that a KArgumentError is raised when the value is not in choices.
        with self.assertRaises(KArgumentError) as error:
            parser.parse_args([0])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument foo: Invalid choice: 0 (value not in choices)")
        self.assertEqual(error.status, 2)

        def too_many_arguments(value, extra):
            return
        # Create the main parser.
        parser = KArgumentParser(exit_on_error=False)
        # Add an argument to the parser.
        parser.add_argument("foo", choices=too_many_arguments, type=int)
        # Check that a KProgramError is raised when a function given to choices that takes more than one argument.
        with self.assertRaises(KProgramError) as error:
            parser.parse_args([0])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument foo: Choices only supports the passing of zero or one argument.")
        self.assertEqual(error.status, 70)

    def test_invalid_value(self):
        # Create the main parser.
        parser = KArgumentParser(exit_on_error=False)
        # Add an argument to the parser.
        argument = parser.add_argument("foo", type=int)
        # Change the type to be uncallable.
        argument.type = "uncallable"
        # Check that a KProgramError is raised when the type is not callable.
        with self.assertRaises(KProgramError) as error:
            parser.parse_args([0])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument foo: uncallable is not callable.")
        self.assertEqual(error.status, 70)

        # Create the main parser.
        parser = KArgumentParser(exit_on_error=False)
        # Add an argument to the parser.
        parser.add_argument("foo", type=int)
        # Check that a KArgumentError is raised when the type conversion fails.
        with self.assertRaises(KArgumentError) as error:
            parser.parse_args(["bar"])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument foo: Invalid value: bar")
        self.assertEqual(error.status, 2)

    def test_not_allowed_with_argument(self):
        # Create a mutually exclusive group.
        group = self.parser.add_mutually_exclusive_group(required=True)
        # Add arguments to the group.
        group.add_argument("-f", "--foo", action="store_true")
        group.add_argument("-b", "--bar", action="store_false")
        # Check that a KUsageError is raised when an argument isn't allowed with another argument.
        with self.assertRaises(KUsageError) as error:
            self.parser.parse_args(["-f","-b"])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument -b/--bar: Not allowed with argument -f/--foo")
        self.assertEqual(error.status, 1)

    def test_ignored_explicit_argument(self):
        # Add arguments to the parser.
        self.parser.add_argument("-f", "--foo", action="store_true")
        self.parser.add_argument("-b", "--bar", action="store_false")
        # Check that a KUsageError is raised when the short arguments are seperated with hypens.
        with self.assertRaises(KUsageError) as error:
            self.parser.parse_args(["-f-b"])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument -f/--foo: Ignored explicit argument '-b'")
        self.assertEqual(error.status, 1)

    def test_expected_argument(self):
        # Create the main parser.
        parser = KArgumentParser(exit_on_error=False)
        # Add an argument to the parser.
        parser.add_argument("-f", "--foo")
        # Check that a KUsageError is raised when one argument is expected.
        with self.assertRaises(KUsageError) as error:
            parser.parse_args(["-f"])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument -f/--foo: Expected one argument.")
        self.assertEqual(error.status, 1)

        # This error is not possible to throw.
        # The regular expression for nargs="?" will always return a match.
        # This error can only be thrown if there is no match.

        # Create the main parser.
        #parser = KArgumentParser(exit_on_error=False)
        # Add an argument to the parser.
        #parser.add_argument("-f", "--foo", nargs="?")
        # Check that a KUsageError is raised when zero or one argument is expected.
        #with self.assertRaises(KUsageError) as error:
        #    parser.parse_args(["-f","value","value"])
        # Check the error message and exit code.
        #error = error.exception
        #self.assertEqual(error.message, "Argument -f/--foo: Expected at most one argument.")
        #self.assertEqual(error.status, 1)

        # Create the main parser.
        parser = KArgumentParser(exit_on_error=False)
        # Add an argument to the parser.
        parser.add_argument("-f", "--foo", nargs="+")
        # Check that a KUsageError is raised when at least one argument is expected.
        with self.assertRaises(KUsageError) as error:
            parser.parse_args(["-f"])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument -f/--foo: Expected at least one argument.")
        self.assertEqual(error.status, 1)

        # Create the main parser.
        parser = KArgumentParser(exit_on_error=False)
        # Add an argument to the parser.
        parser.add_argument("-f", "--foo", nargs=1)
        # Check that a KUsageError is raised when N arguments are expected.
        with self.assertRaises(KUsageError) as error:
            parser.parse_args(["-f"])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument -f/--foo: Expected 1 argument.")
        self.assertEqual(error.status, 1)

        # Create the main parser.
        parser = KArgumentParser(exit_on_error=False)
        # Add an argument to the parser.
        parser.add_argument("-f", "--foo", nargs=2)
        # Check that a KUsageError is raised when N arguments are expected.
        with self.assertRaises(KUsageError) as error:
            parser.parse_args(["-f"])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument -f/--foo: Expected 2 arguments.")
        self.assertEqual(error.status, 1)

    def test_conflicting_option_strings(self):
        # Create the main parser.
        parser = KArgumentParser(exit_on_error=False)
        # Add an argument to the parser.
        parser.add_argument("-f", "--foo")
        # Check that a KProgramError is raised when there are conflicting option strings.
        with self.assertRaises(KProgramError) as error:
            parser.add_argument("-f", "--bar")
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument -f/--bar: Conflicting option string: -f")
        self.assertEqual(error.status, 70)

        # Create the main parser.
        parser = KArgumentParser(exit_on_error=False)
        # Add an argument to the parser.
        parser.add_argument("-f", "--foo")
        # Check that a KProgramError is raised when there are conflicting option strings.
        with self.assertRaises(KProgramError) as error:
            parser.add_argument("-f", "--foo")
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument -f/--foo: Conflicting option strings: -f, --foo")
        self.assertEqual(error.status, 70)

    def test_filetype(self):
        # Add the type FileType("r") to allowed_types.
        self.parser.modify_allowed_types(add={"FileType('r')" : "file"})
        # Add an argument to the parser.
        self.parser.add_argument("foo", type=FileType("r"))
        # Check that a KArgumentError is raised when there is problem with the filetype.
        with self.assertRaises(KArgumentError) as error:
            self.parser.parse_args(["file_does_not_exist"])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Argument foo: Can't open 'file_does_not_exist': OSError: [Errno 2] No such file or directory: 'file_does_not_exist'")
        self.assertEqual(error.status, 2)

    def test_fromfile_prefix_chars(self):
        # Create the main parser.
        parser = KArgumentParser(exit_on_error=False, fromfile_prefix_chars="#")
        # Add an argument to the parser.
        parser.add_argument("foo")
        # Check that a KArgumentError is raised when there is problem with a file given for argument processing.
        with self.assertRaises(KArgumentError) as error:
            parser.parse_args(["#file_does_not_exist"])
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "OSError: [Errno 2] No such file or directory: 'file_does_not_exist'")
        self.assertEqual(error.status, 2)

    def test_error(self):
        # Check that a KProgramError is raised when error() is called with no message.
        with self.assertRaises(KProgramError) as error:
            self.parser.error(None)
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Undefined error message. That should not happen. Message: None")
        self.assertEqual(error.status, 70)

        # Check that a KProgramError is raised when error() is called with a message that doesn't get handled.
        with self.assertRaises(KProgramError) as error:
            self.parser.error("This message will fail.")
        # Check the error message and exit code.
        error = error.exception
        self.assertEqual(error.message, "Undefined error message. That should not happen. Message: This message will fail.")
        self.assertEqual(error.status, 70)

if __name__ == "__main__":
    unittest.main()

