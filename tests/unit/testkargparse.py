#!/usr/bin/env python3

from kargparse.parser import ArgumentParser, HelpFormatter, KArgumentParser
import unittest

__usage__ = "testkargparse.py mode-0[1-4] [options] {-c|--count} <store_me> [<store_me> [...]]"

__description__ = """
Give me detail about what this code is going to do. That could be an
explanation of the whole package, or more explicit detail of how to use
the arguments.
"""

__epilog__ = """
Give me additional detail about this code after the description of
arguments. That could be an additional note, or something simple like
a goodbye message.
"""

basic_expected_usage = """
Usage: testkargparse.py [options] {-c|--count} <store_me> [<store_me> [...]]

"""

basic_expected_help = """
Usage: testkargparse.py [options] {-c|--count} <store_me> [<store_me> [...]]

Positional Arguments:
    <store_me> [<store_me> [...]]
        Give me something to store.

Additional Required Arguments and/or Options:
    {-a|--append} <integer>                                          (optional) 
        I can be specified multiple times.

    {-c|--count}                                                     (required) 
        I count the number of times this argument is specified.

    {-f|--store-false}                                               (optional) 
        I'm a flag that stores False.

    {-h|--help}                                                      (optional) 
        I'm the argument to see the help statement.

    {-p|--append-a-const}                                            (optional) 
        I'm a flag that appends a constant each time I'm specified.

    {-s|--store-const}                                               (optional) 
        I'm a flag that stores a constant.

    {--store} <string> <string>                                      (optional) 
        Give me something to store.

    {-t|--store-true}                                                (optional) 
        I'm a flag that stores True.

    {-v|--version}                                                   (optional) 
        I'm the version of this script.

"""

moderate_expected_usage = """
Usage: testkargparse.py [options] {mode-01|mode-02} ...


Usage: testkargparse.py mode-01 [options] <store_me> [<store_me> [...]]


Usage: testkargparse.py mode-02 [options] {-c|--count}

"""

moderate_expected_help = """
Usage: testkargparse.py [options] {mode-01|mode-02} ...

Description:
    Give me detail about what this code is going to do. That could be an
    explanation of the whole package, or more explicit detail of how to use
    the arguments.

Positional Arguments:
    {mode-01|mode-02} ...
        Modes of Operation.

        <mode-01>
            I'm a mode containing my own set of arguments.

        <mode-02>
            I'm a mode containing my own set of arguments.

Additional Required Arguments and/or Options:
    {-h|--help}                                                      (optional) 
        I'm the argument to see the help statement.


Usage: testkargparse.py mode-01 [options] <store_me> [<store_me> [...]]

Description:
    Give me detail about what this code is going to do. That could be an
    explanation of the whole package, or more explicit detail of how to use
    the arguments.

Positional Arguments:
    <store_me> [<store_me> [...]]
        Give me something to store.

Additional Required Arguments and/or Options:
    {-f|--store-false}                                               (optional) 
        I'm a flag that stores False.

    {-s|--store-const}                                               (optional) 
        I'm a flag that stores a constant.

    {--store} <string> <string>                                      (optional) 
        Give me something to store.

    {-t|--store-true}                                                (optional) 
        I'm a flag that stores True.


Usage: testkargparse.py mode-02 [options] {-c|--count}

Description:
    Give me detail about what this code is going to do. That could be an
    explanation of the whole package, or more explicit detail of how to use
    the arguments.

Additional Required Arguments and/or Options:
    {-a|--append} <integer>                                          (optional) 
        I can be specified multiple times.

    {-c|--count}                                                     (required) 
        I count the number of times this argument is specified.

    {-h|--help}                                                      (optional) 
        I'm the argument to see the help statement.

    {-p|--append-a-const}                                            (optional) 
        I'm a flag that appends a constant each time I'm specified.

    {-v|--version}                                                   (optional) 
        I'm the version of this script.

"""

complex_expected_usage = """
Usage: testkargparse.py [options] {mode-01|mode-02|mode-03|mode-04} ...


Usage: testkargparse.py mode-0[1-4] [options] {-c|--count} <store_me> [<store_me> [...]]

"""

complex_expected_help = """
Usage: testkargparse.py [options] {mode-01|mode-02|mode-03|mode-04} ...

Description:
    Give me detail about what this code is going to do. That could be an
    explanation of the whole package, or more explicit detail of how to use
    the arguments.

Positional Arguments:
    {mode-01|mode-02|mode-03|mode-04} ...
        Modes of Operation.

        <mode-01>
            I'm a mode containing my own set of arguments.

        <mode-02>
            I'm a mode containing my own set of arguments.

        <mode-03>
            I'm a mode containing my own set of arguments.

        <mode-04>
            I'm a mode containing my own set of arguments.

Additional Required Arguments and/or Options:
    {-h|--help}                                                      (optional) 
        I'm the argument to see the help statement.

Epilog:
    Give me additional detail about this code after the description of
    arguments. That could be an additional note, or something simple like a
    goodbye message.


Usage: testkargparse.py mode-0[1-4] [options] {-c|--count} <store_me> [<store_me> [...]]

Description:
    Give me detail about what this code is going to do. That could be an
    explanation of the whole package, or more explicit detail of how to use
    the arguments.

Positional Arguments:
    <store_me> [<store_me> [...]]
        Give me something to store.

Additional Required Arguments and/or Options:
    {-a|--append} <integer>                                          (optional) 
        I can be specified multiple times.

    {-c|--count}                                                     (required) 
        I count the number of times this argument is specified.

    {-f|--store-false}                                               (optional) 
        I'm a flag that stores False.

    {-h|--help}                                                      (optional) 
        I'm the argument to see the help statement.

    {-p|--append-a-const}                                            (optional) 
        I'm a flag that appends a constant each time I'm specified.

    {-s|--store-const}                                               (optional) 
        I'm a flag that stores a constant.

    {--store} <string> <string>                                      (optional) 
        Give me something to store.

    {-t|--store-true}                                                (optional) 
        I'm a flag that stores True.

    {-v|--version}                                                   (optional) 
        I'm the version of this script.

Epilog:
    Give me additional detail about this code after the description of
    arguments. That could be an additional note, or something simple like a
    goodbye message.

"""

class TestKArgParse(unittest.TestCase):

    def setUp(self):
        # This unittest attribute forces the whole diff to be shown when it is None.
        self.maxDiff = None
        # Create a parser using kargparse's default formatter_class (KHelpFormatter).
        self.actual_parser = KArgumentParser(add_help=False, exit_on_error=False)
        # Create a parser using argparse's default formatter_class (HelpFormatter).
        self.legacy_parser = KArgumentParser(add_help=False, exit_on_error=False, formatter_class=HelpFormatter)
        # Create a parser using argparse's ArgumentParser.
        self.target_parser = ArgumentParser(add_help=False)

    def test_basic_parser(self):
        # Add arguments to the actual parser.
        self.actual_parser.add_argument("store", action="store", metavar="store_me", nargs="+", type=str, help="Give me something to store.")
        self.actual_parser.add_argument("--store", action="store", default="default", nargs=2, type=str, help="Give me something to store.")
        self.actual_parser.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        self.actual_parser.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        self.actual_parser.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        self.actual_parser.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        self.actual_parser.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        self.actual_parser.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        self.actual_parser.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        self.actual_parser.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Add arguments to the legacy parser.
        self.legacy_parser.add_argument("store", action="store", metavar="store_me", nargs="+", type=str, help="Give me something to store.")
        self.legacy_parser.add_argument("--store", action="store", default="default", nargs=2, type=str, help="Give me something to store.")
        self.legacy_parser.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        self.legacy_parser.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        self.legacy_parser.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        self.legacy_parser.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        self.legacy_parser.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        self.legacy_parser.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        self.legacy_parser.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        self.legacy_parser.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Add arguments to the target parser.
        self.target_parser.add_argument("store", action="store", metavar="store_me", nargs="+", type=str, help="Give me something to store.")
        self.target_parser.add_argument("--store", action="store", default="default", nargs=2, type=str, help="Give me something to store.")
        self.target_parser.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        self.target_parser.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        self.target_parser.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        self.target_parser.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        self.target_parser.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        self.target_parser.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        self.target_parser.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        self.target_parser.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Check that the actual_parser's usage statement matches the expected usage statement.
        self.assertEqual(self.actual_parser.format_usage(), basic_expected_usage)
        # Check that the actual_parser's help statement matches the expected help statement.
        self.assertEqual(self.actual_parser.format_help(), basic_expected_help)

        # Check that the legacy_parser's usage statement matches the target_parser's usage statement.
        self.assertEqual(self.legacy_parser.format_usage(), self.target_parser.format_usage())
        # Check that the legacy_parser's help statement matches the target_parser's help statement.
        self.assertEqual(self.legacy_parser.format_help(), self.target_parser.format_help())

    def test_moderate_parser(self):
        # Give the parsers a description.
        self.actual_parser.description = __description__
        self.legacy_parser.description = __description__
        self.target_parser.description = __description__

        # Prepare the parsers for subparsers.
        actual_subparsers = self.actual_parser.add_subparsers(dest='mode', help="Modes of Operation.")
        legacy_subparsers = self.legacy_parser.add_subparsers(dest='mode', help="Modes of Operation.")
        target_subparsers = self.target_parser.add_subparsers(dest='mode', help="Modes of Operation.")

        # Create a dictionary of common subparser arguments.
        common_subparser_arguments = {"add_help" : False, "description" : __description__, "help" : "I'm a mode containing my own set of arguments."}

        # Add subparsers to the actual parser.
        actual_subparser_01 = actual_subparsers.add_parser("mode-01", **common_subparser_arguments)
        actual_subparser_02 = actual_subparsers.add_parser("mode-02", **common_subparser_arguments)

        # Add subparsers to the legacy parser.
        legacy_subparser_01 = legacy_subparsers.add_parser("mode-01", formatter_class=HelpFormatter, **common_subparser_arguments)
        legacy_subparser_02 = legacy_subparsers.add_parser("mode-02", formatter_class=HelpFormatter, **common_subparser_arguments)

        # Add subparsers to the target parser.
        target_subparser_01 = target_subparsers.add_parser("mode-01", **common_subparser_arguments)
        target_subparser_02 = target_subparsers.add_parser("mode-02", **common_subparser_arguments)

        # Add arguments to the actual parser.
        self.actual_parser.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")
        actual_subparser_01.add_argument("store", action="store", metavar="store_me", nargs="+", type=str, help="Give me something to store.")
        actual_subparser_01.add_argument("--store", action="store", default="default", nargs=2, type=str, help="Give me something to store.")
        actual_subparser_01.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        actual_subparser_01.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        actual_subparser_01.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        actual_subparser_02.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        actual_subparser_02.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        actual_subparser_02.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        actual_subparser_02.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        actual_subparser_02.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Add arguments to the legacy parser.
        self.legacy_parser.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")
        legacy_subparser_01.add_argument("store", action="store", metavar="store_me", nargs="+", type=str, help="Give me something to store.")
        legacy_subparser_01.add_argument("--store", action="store", default="default", nargs=2, type=str, help="Give me something to store.")
        legacy_subparser_01.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        legacy_subparser_01.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        legacy_subparser_01.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        legacy_subparser_02.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        legacy_subparser_02.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        legacy_subparser_02.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        legacy_subparser_02.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        legacy_subparser_02.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Add arguments to the target parser.
        self.target_parser.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")
        target_subparser_01.add_argument("store", action="store", metavar="store_me", nargs="+", type=str, help="Give me something to store.")
        target_subparser_01.add_argument("--store", action="store", default="default", nargs=2, type=str, help="Give me something to store.")
        target_subparser_01.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        target_subparser_01.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        target_subparser_01.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        target_subparser_02.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        target_subparser_02.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        target_subparser_02.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        target_subparser_02.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        target_subparser_02.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Check that the actual_parser's usage statement matches the expected usage statement.
        self.assertEqual(self.actual_parser.format_usage() + actual_subparser_01.format_usage() + actual_subparser_02.format_usage(), moderate_expected_usage)
        # Check that the actual_parser's help statement matches the expected help statement.
        self.assertEqual(self.actual_parser.format_help() + actual_subparser_01.format_help() + actual_subparser_02.format_help(), moderate_expected_help)

        # Check that the legacy_parser's usage statement matches the target_parser's usage statement.
        self.assertEqual(self.legacy_parser.format_usage(), self.target_parser.format_usage())
        self.assertEqual(legacy_subparser_01.format_usage(), target_subparser_01.format_usage())
        self.assertEqual(legacy_subparser_02.format_usage(), target_subparser_02.format_usage())
        # Check that the legacy_parser's help statement matches the target_parser's help statement.
        self.assertEqual(self.legacy_parser.format_help(), self.target_parser.format_help())
        self.assertEqual(legacy_subparser_01.format_help(), target_subparser_01.format_help())
        self.assertEqual(legacy_subparser_02.format_help(), target_subparser_02.format_help())

    def test_complex_parser(self):
        # Give the parsers a description.
        self.actual_parser.description = __description__
        self.legacy_parser.description = __description__
        self.target_parser.description = __description__

        # Give the parsers a epilog.
        self.actual_parser.epilog = __epilog__
        self.legacy_parser.epilog = __epilog__
        self.target_parser.epilog = __epilog__

        # Prepare the parsers for subparsers.
        actual_subparsers = self.actual_parser.add_subparsers(dest='mode', help="Modes of Operation.")
        legacy_subparsers = self.legacy_parser.add_subparsers(dest='mode', help="Modes of Operation.")
        target_subparsers = self.target_parser.add_subparsers(dest='mode', help="Modes of Operation.")

        # Prepare the actual parser for parents.
        actual_parent_01 = KArgumentParser(add_help=False)
        actual_parent_02 = KArgumentParser(add_help=False)
        actual_parent_03 = KArgumentParser(add_help=False)
        actual_parent_04 = KArgumentParser(add_help=False)

        # Prepare the legacy parser for parents.
        legacy_parent_01 = KArgumentParser(add_help=False, formatter_class=HelpFormatter)
        legacy_parent_02 = KArgumentParser(add_help=False, formatter_class=HelpFormatter)
        legacy_parent_03 = KArgumentParser(add_help=False, formatter_class=HelpFormatter)
        legacy_parent_04 = KArgumentParser(add_help=False, formatter_class=HelpFormatter)

        # Prepare the target parser for parents.
        target_parent_01 = ArgumentParser(add_help=False)
        target_parent_02 = ArgumentParser(add_help=False)
        target_parent_03 = ArgumentParser(add_help=False)
        target_parent_04 = ArgumentParser(add_help=False)

        # Add arguments to the actual parser's parents.
        actual_parent_01.add_argument("store", action="store", metavar="store_me", nargs="+", type=str, help="Give me something to store.")
        actual_parent_01.add_argument("--store", action="store", default="default", nargs=2, type=str, help="Give me something to store.")
        actual_parent_02.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        actual_parent_02.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        actual_parent_03.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        actual_parent_03.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        actual_parent_03.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        actual_parent_04.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        actual_parent_04.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        actual_parent_04.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Add arguments to the legacy parser's parents.
        legacy_parent_01.add_argument("store", action="store", metavar="store_me", nargs="+", type=str, help="Give me something to store.")
        legacy_parent_01.add_argument("--store", action="store", default="default", nargs=2, type=str, help="Give me something to store.")
        legacy_parent_02.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        legacy_parent_02.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        legacy_parent_03.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        legacy_parent_03.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        legacy_parent_03.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        legacy_parent_04.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        legacy_parent_04.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        legacy_parent_04.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Add arguments to the target parser's parents.
        target_parent_01.add_argument("store", action="store", metavar="store_me", nargs="+", type=str, help="Give me something to store.")
        target_parent_01.add_argument("--store", action="store", default="default", nargs=2, type=str, help="Give me something to store.")
        target_parent_02.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        target_parent_02.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        target_parent_03.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        target_parent_03.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        target_parent_03.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        target_parent_04.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        target_parent_04.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        target_parent_04.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Create a list of parents for the parsers.
        actual_parents = [actual_parent_01, actual_parent_02, actual_parent_03, actual_parent_04]
        legacy_parents = [legacy_parent_01, legacy_parent_02, legacy_parent_03, legacy_parent_04]
        target_parents = [target_parent_01, target_parent_02, target_parent_03, target_parent_04]

        # Create a dictionary of common subparser arguments.
        common_subparser_arguments = {"add_help" : False, "description" : __description__, "epilog" : __epilog__, "usage" : __usage__, "help" : "I'm a mode containing my own set of arguments."}

        # Add subparsers to the actual parser.
        actual_subparser_01 = actual_subparsers.add_parser("mode-01", parents=actual_parents[:1], **common_subparser_arguments)
        actual_subparser_02 = actual_subparsers.add_parser("mode-02", parents=actual_parents[:2], **common_subparser_arguments)
        actual_subparser_03 = actual_subparsers.add_parser("mode-03", parents=actual_parents[:3], **common_subparser_arguments)
        actual_subparser_04 = actual_subparsers.add_parser("mode-04", parents=actual_parents[:4], **common_subparser_arguments)

        # Add subparsers to the legacy parser.
        legacy_subparser_01 = legacy_subparsers.add_parser("mode-01", parents=legacy_parents[:1], formatter_class=HelpFormatter, **common_subparser_arguments)
        legacy_subparser_02 = legacy_subparsers.add_parser("mode-02", parents=legacy_parents[:2], formatter_class=HelpFormatter, **common_subparser_arguments)
        legacy_subparser_03 = legacy_subparsers.add_parser("mode-03", parents=legacy_parents[:3], formatter_class=HelpFormatter, **common_subparser_arguments)
        legacy_subparser_04 = legacy_subparsers.add_parser("mode-04", parents=legacy_parents[:4], formatter_class=HelpFormatter, **common_subparser_arguments)

        # Add subparsers to the target parser.
        target_subparser_01 = target_subparsers.add_parser("mode-01", parents=target_parents[:1], **common_subparser_arguments)
        target_subparser_02 = target_subparsers.add_parser("mode-02", parents=target_parents[:2], **common_subparser_arguments)
        target_subparser_03 = target_subparsers.add_parser("mode-03", parents=target_parents[:3], **common_subparser_arguments)
        target_subparser_04 = target_subparsers.add_parser("mode-04", parents=target_parents[:4], **common_subparser_arguments)

        # Add arguments to the actual parser.
        self.actual_parser.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")
        actual_subparser_01.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        actual_subparser_01.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        actual_subparser_01.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        actual_subparser_01.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        actual_subparser_01.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        actual_subparser_01.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        actual_subparser_01.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        actual_subparser_01.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")
        actual_subparser_02.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        actual_subparser_02.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        actual_subparser_02.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        actual_subparser_02.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        actual_subparser_02.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        actual_subparser_02.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")
        actual_subparser_03.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        actual_subparser_03.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        actual_subparser_03.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Add arguments to the legacy parser.
        self.legacy_parser.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")
        legacy_subparser_01.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        legacy_subparser_01.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        legacy_subparser_01.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        legacy_subparser_01.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        legacy_subparser_01.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        legacy_subparser_01.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        legacy_subparser_01.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        legacy_subparser_01.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")
        legacy_subparser_02.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        legacy_subparser_02.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        legacy_subparser_02.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        legacy_subparser_02.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        legacy_subparser_02.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        legacy_subparser_02.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")
        legacy_subparser_03.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        legacy_subparser_03.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        legacy_subparser_03.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Add arguments to the target parser.
        self.target_parser.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")
        target_subparser_01.add_argument("-s", "--store-const", action="store_const", const=0, help="I'm a flag that stores a constant.")
        target_subparser_01.add_argument("-t", "--store-true", action="store_true", help="I'm a flag that stores True.")
        target_subparser_01.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        target_subparser_01.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        target_subparser_01.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        target_subparser_01.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        target_subparser_01.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        target_subparser_01.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")
        target_subparser_02.add_argument("-f", "--store-false", action="store_false", help="I'm a flag that stores False.")
        target_subparser_02.add_argument("-a", "--append", action="append", choices=[1,2,3,4,5], default=3, type=int, help="I can be specified multiple times.")
        target_subparser_02.add_argument("-p", "--append-a-const", action="append_const", const="constant", dest="const", help="I'm a flag that appends a constant each time I'm specified.")
        target_subparser_02.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        target_subparser_02.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        target_subparser_02.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")
        target_subparser_03.add_argument("-c", "--count", action="count", required=True, help="I count the number of times this argument is specified.")
        target_subparser_03.add_argument("-v", "--version", action="version", version="0", help="I'm the version of this script.")
        target_subparser_03.add_argument("-h", "--help", action="help", help="I'm the argument to see the help statement.")

        # Check that the actual_parser's usage statement matches the expected usage statement.
        self.assertEqual(self.actual_parser.format_usage() + actual_subparser_01.format_usage(), complex_expected_usage)
        self.assertEqual(actual_subparser_01.format_usage(), actual_subparser_02.format_usage())
        self.assertEqual(actual_subparser_02.format_usage(), actual_subparser_03.format_usage())
        self.assertEqual(actual_subparser_03.format_usage(), actual_subparser_04.format_usage())
        # Check that the actual_parser's help statement matches the expected help statement.
        self.assertEqual(self.actual_parser.format_help() + actual_subparser_01.format_help(), complex_expected_help)
        self.assertEqual(actual_subparser_01.format_help(), actual_subparser_02.format_help())
        self.assertEqual(actual_subparser_02.format_help(), actual_subparser_03.format_help())
        self.assertEqual(actual_subparser_03.format_help(), actual_subparser_04.format_help())

        # Check that the legacy_parser's usage statement matches the target_parser's usage statement.
        self.assertEqual(self.legacy_parser.format_usage() + legacy_subparser_01.format_usage() + legacy_subparser_02.format_usage() + legacy_subparser_03.format_usage() + legacy_subparser_04.format_usage(),
                         self.target_parser.format_usage() + target_subparser_01.format_usage() + target_subparser_02.format_usage() + target_subparser_03.format_usage() + target_subparser_04.format_usage())
        self.assertEqual(legacy_subparser_01.format_usage(), legacy_subparser_02.format_usage())
        self.assertEqual(legacy_subparser_02.format_usage(), legacy_subparser_03.format_usage())
        self.assertEqual(legacy_subparser_03.format_usage(), legacy_subparser_04.format_usage())
        # Check that the legacy_parser's help statement matches the target_parser's help statement.
        self.assertEqual(self.legacy_parser.format_help() + legacy_subparser_01.format_help() + legacy_subparser_02.format_help() + legacy_subparser_03.format_help() + legacy_subparser_04.format_help(),
                         self.target_parser.format_help() + target_subparser_01.format_help() + target_subparser_02.format_help() + target_subparser_03.format_help() + target_subparser_04.format_help())
        self.assertEqual(legacy_subparser_01.format_help(), legacy_subparser_02.format_help())
        self.assertEqual(legacy_subparser_02.format_help(), legacy_subparser_03.format_help())
        self.assertEqual(legacy_subparser_03.format_help(), legacy_subparser_04.format_help())

if __name__ == "__main__":
    unittest.main()

