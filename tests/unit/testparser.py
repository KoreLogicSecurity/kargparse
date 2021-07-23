#!/usr/bin/env python3

from kargparse.parser import ArgumentError, FileType, KArgumentParser, KArgumentError, KProgramError, KUsageError, Namespace
from re import match
import unittest

class TestParser(unittest.TestCase):

    def setUp(self):
        # Create the main parser.
        self.parser = KArgumentParser(add_help=False, exit_on_error=False)

    def test_get_allowed_types(self):
        # Attempt to get the allowed_types dictionary.
        allowed_types = self.parser.get_allowed_types()
        # Check the allowed_types dictionary.
        self.assertEqual(allowed_types, {"str" : "string", "int" : "integer"})

    def test_modify_allowed_types(self):
        # Attempt to set the allowed_types dictionary.
        self.parser.modify_allowed_types(set={"str" : "string"})
        # Check the allowed_types dictionary.
        self.assertEqual(self.parser.get_allowed_types(), {"str" : "string"})

        # Attempt to add to the allowed_types dictionary.
        self.parser.modify_allowed_types(add={"int" : "integer"})
        # Check the allowed_types dictionary.
        self.assertEqual(self.parser.get_allowed_types(), {"str" : "string", "int" : "integer"})

        # Attempt to replace a type in the allowed_types dictionary.
        self.parser.modify_allowed_types(replace={"str" : "str"})
        # Check the allowed_types dictionary.
        self.assertEqual(self.parser.get_allowed_types(), {"str" : "str", "int" : "integer"})

        # Attempt to delete a type in the allowed_types dictionary.
        self.parser.modify_allowed_types(delete=["str"])
        # Check the allowed_types dictionary.
        self.assertEqual(self.parser.get_allowed_types(), {"int" : "integer"})

        # Check to make sure a ValueError is raised for set, add, and replace when a type can't be converted to a dictionary.
        with self.assertRaises(ValueError) as error:
            self.parser.modify_allowed_types(set="string")
        with self.assertRaises(ValueError) as error:
            self.parser.modify_allowed_types(add="string")
        with self.assertRaises(ValueError) as error:
            self.parser.modify_allowed_types(replace="string")

        # Check to make sure a TypeError is raised for delete when a type can't be converted to a list.
        with self.assertRaises(TypeError) as error:
            self.parser.modify_allowed_types(delete=0)

        # Check that only the proper keyword arguments set the allowed_types dictionary.
        self.parser.modify_allowed_types(foo={"str" : "string"})
        self.assertEqual(self.parser.get_allowed_types(), {"int" : "integer"})

    def test_get_error_codes(self):
        # Attempt to get the error_codes dictionary.
        error_codes = self.parser.get_error_codes()
        # Check the error_codes dictionary.
        self.assertEqual(error_codes, {"argument" : 2, "program" : 70, "usage" : 1})

    def test_modify_error_codes(self):
        # Attempt to modify the error_codes dictionary.
        self.parser.modify_error_codes(argument=3, program=71, usage=2)
        # Check the error_codes dictionary.
        self.assertEqual(self.parser.get_error_codes(), {"argument" : 3, "program" : 71, "usage" : 2})

        # Check to make sure a ValueError is raised when an error code can't be converted to an integer.
        with self.assertRaises(ValueError) as error:
            self.parser.modify_error_codes(argument="foo")

        # Check that only the proper keyword arguments set the error_codes dictionary.
        self.parser.modify_error_codes(argument=2, program=70, foo=1)
        self.assertEqual(self.parser.get_error_codes(), {"argument" : 2, "program" : 70, "usage" : 2})

    def test_format_help(self):
        # Add a few arguments to the parser.
        self.parser.add_argument("foo", help="This is the help for foo.")
        self.parser.add_argument("-b", "--bar", help="This is the help for -b|--bar.")
        # Format the help statement.
        help = self.parser.format_help()
        # Check to make sure the same help statement is reproduced.
        self.assertEqual(help, self.parser.format_help())

    def test_get_formatter(self):
        # Attempt to get the formatter.
        formatter = self.parser._get_formatter()
        # Check to make sure a formatter is reproduced with the same arguments.
        self.assertEqual(formatter._prog, self.parser._get_formatter()._prog)
        self.assertEqual(formatter._allowed_types, self.parser._get_formatter()._allowed_types)
        self.assertEqual(formatter._indent_increment, self.parser._get_formatter()._indent_increment)
        self.assertEqual(formatter._max_help_position, self.parser._get_formatter()._max_help_position)
        self.assertEqual(formatter._width, self.parser._get_formatter()._width)
        self.assertEqual(formatter._delimeter, self.parser._get_formatter()._delimeter)
        self.assertEqual(formatter._prefix_chars, self.parser._get_formatter()._prefix_chars)

    def test_check_value(self):
        # Add an argument to the parser.
        foo = self.parser.add_argument("foo", choices="abcde")
        # Check to make sure the value is in the choices (None means the test passed).
        self.assertEqual(self.parser._check_value(foo, "a"), None)
        # Change the choices.
        foo.choices = [1,2,3,4,5]
        # Check to make sure the value is in the choices (None means the test passed).
        self.assertEqual(self.parser._check_value(foo, 3), None)
        # Change the choices.
        foo.choices = range(0,10,2)
        # Check to make sure the value is in the choices (None means the test passed).
        self.assertEqual(self.parser._check_value(foo, 8), None)
        # Change the choices.
        foo.choices = lambda value: "bar" in value
        # Check to make sure the value is in the choices (None means the test passed).
        self.assertEqual(self.parser._check_value(foo, "foobar"), None)
        # Change the choices.
        foo.choices = lambda value: value % 3 == 0 and value / 2 == 6
        # Check to make sure the value is in the choices (None means the test passed).
        self.assertEqual(self.parser._check_value(foo, 12), None)
        # Change the choices.
        foo.choices = lambda value: match("^foobar$", value)
        # Check to make sure the value is in the choices (None means the test passed).
        self.assertEqual(self.parser._check_value(foo, "foobar"), None)
        # Create a function to check if the value is in choices.
        def check_value(value):
            return "foo" in value or "bar" in value and "baz" in value
        # Change the choices.
        foo.choices = check_value
        # Check to make sure the value is in the choices (None means the test passed).
        self.assertEqual(self.parser._check_value(foo, "foobaz"), None)
        # Change the choices.
        foo.choices = check_value
        # Check to make sure the value is in the choices (None means the test passed).
        self.assertEqual(self.parser._check_value(foo, "barbaz"), None)

        # Check that an ArgumentError is raised where there is an invalid choice.
        foo.choices = [1,2,3,4,5]
        with self.assertRaises(ArgumentError) as error:
            self.parser._check_value(foo, 0)
        # Check the error message.
        error = error.exception
        self.assertEqual(error.message, "Invalid choice: 0 (choose from 1, 2, 3, 4, 5)")

        # Check that an ArgumentError is raised where there is an invalid choice.
        foo.choices = [i for i in range(1, 100)]
        with self.assertRaises(ArgumentError) as error:
            self.parser._check_value(foo, 0)
        # Check the error message.
        error = error.exception
        self.assertEqual(error.message, "Invalid choice: 0 (value not in choices)")

        # Check that an ArgumentError is raised when an invalid function passed.
        def check_value(value, foo=[1,2,3,4,5]):
            return value in foo
        foo.choices = check_value
        with self.assertRaises(ArgumentError) as error:
            self.parser._check_value(foo, 0)
        # Check the error message.
        error = error.exception
        self.assertEqual(error.message, "Choices only supports the passing of zero or one argument.")

    def test_get_value(self):
        # Add to the allowed_types dictionary.
        self.parser.modify_allowed_types(add={"foo" : "foo", "custom" : "custom"})
        # Add an argument to the parser.
        foo = self.parser.add_argument("foo", type=int)
        # Check to make sure the value is converted to the proper type.
        self.assertEqual(self.parser._get_value(foo, "0"), 0)
        # Check to make sure an ArgumentError is raised when the type conversion fails.
        with self.assertRaises(ArgumentError) as error:
            self.parser._get_value(foo, "foo")
        # Check the error message.
        error = error.exception
        self.assertEqual(error.message, "Invalid value: foo")

        def custom(value):
            return [word.lower() for word in value.split(",")]
        # Change the type.
        foo.type = custom
        # Check to make sure the value is converted to the proper type.
        self.assertEqual(self.parser._get_value(foo, "foO,bar,Baz"), ["foo", "bar", "baz"])

        # Change the type.
        foo.type = "foo"
        # Check to make sure an ArgumentError is raised when the type is not callable.
        with self.assertRaises(ArgumentError) as error:
            self.parser._get_value(foo, "foo")
        # Check the error message.
        error = error.exception
        self.assertEqual(error.message, "foo is not callable.")

    def test_add_argument(self):
        # Check to make sure different types of arguments and parameters work.
        self.parser.add_argument("store", action="store", metavar="store_me", nargs="+", type=str, help="Give me something to store.")
        self.parser.add_argument("--store", action="store", default="default", nargs=2, type=str, help="Give me something to store.")
        self.parser.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        self.parser.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        self.parser.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        self.parser.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        self.parser.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        self.parser.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        self.parser.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        self.parser.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Check to make sure an ArgumentError is raised when there is a type that is not in the allowed_types dictionary.
        with self.assertRaises(KProgramError) as error:
            self.parser.add_argument("foo", type=list)
        # Check the error message.
        error = error.exception
        self.assertEqual(error.message, "Argument foo: The specified type 'list' is not supported.")

    def test_parse_known_args(self):
        # Add Arguments to the parser.
        self.parser.add_argument("store", action="store", metavar="store_me", nargs="+", type=str, help="Give me something to store.")
        self.parser.add_argument("--store", action="store", default="default", dest="s", nargs=2, type=str, help="Give me something to store.")
        self.parser.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        self.parser.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        self.parser.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        self.parser.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=[], type=int, help="I can be specified multiple times.")
        self.parser.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="append_const", help="I'm a flag that appends a constant each time I'm specified.")
        self.parser.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        self.parser.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        self.parser.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Attempt to parse the arguments.
        pka = self.parser.parse_known_args
        args = pka(["-c", "foo", "-a", "4", "--store", "baz", "bar"])
        self.assertEqual(str(args), "(Namespace(append=[4], append_const=None, count=1, s=['baz', 'bar'], store=['foo'], store_const=None, store_false=True, store_true=False), [])")
        args = pka(["-c", "-c", "-t", "-f", "bar", "-p", "-s"])
        self.assertEqual(str(args), "(Namespace(append=[], append_const=['constant'], count=2, s='default', store=['bar'], store_const=0, store_false=False, store_true=True), [])")
        args = pka(["-c", "-a", "1", "-a", "5", "foo"])
        self.assertEqual(str(args), "(Namespace(append=[1, 5], append_const=None, count=1, s='default', store=['foo'], store_const=None, store_false=True, store_true=False), [])")
        args = pka(["-c", "-p", "-p", "foo", "bar", "baz"])
        self.assertEqual(str(args), "(Namespace(append=[], append_const=['constant', 'constant'], count=1, s='default', store=['foo', 'bar', 'baz'], store_const=None, store_false=True, store_true=False), [])")
        args = pka(["-c", "-s", "--store", "foo", "bar", "baz"])
        self.assertEqual(str(args), "(Namespace(append=[], append_const=None, count=1, s=['foo', 'bar'], store=['baz'], store_const=0, store_false=True, store_true=False), [])")
        args = pka(["-c", "-s", "--store", "foo", "bar", "baz", "--unknown", "7"])
        self.assertEqual(str(args), "(Namespace(append=[], append_const=None, count=1, s=['foo', 'bar'], store=['baz'], store_const=0, store_false=True, store_true=False), ['--unknown', '7'])")

if __name__ == "__main__":
    unittest.main()

