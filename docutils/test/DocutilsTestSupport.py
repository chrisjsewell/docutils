# Authors:  David Goodger; Garth Kidd
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Exports the following:

:Modules:
    - `statemachine` is 'docutils.statemachine'
    - `nodes` is 'docutils.nodes'
    - `urischemes` is 'docutils.urischemes'
    - `utils` is 'docutils.utils'
    - `transforms` is 'docutils.transforms'
    - `states` is 'docutils.parsers.rst.states'
    - `tableparser` is 'docutils.parsers.rst.tableparser'

:Classes:
    - `CustomTestSuite`
    - `CustomTestCase`
    - `TransformTestSuite`
    - `TransformTestCase`
    - `ParserTestSuite`
    - `ParserTestCase`
    - `PEPParserTestSuite`
    - `PEPParserTestCase`
    - `GridTableParserTestSuite`
    - `GridTableParserTestCase`
    - `SimpleTableParserTestSuite`
    - `SimpleTableParserTestCase`
    - `DevNull` (output sink)
"""
__docformat__ = 'reStructuredText'

import sys
import os
import unittest
import difflib
import inspect
from pprint import pformat
from types import UnicodeType
import package_unittest
import docutils
from docutils import frontend, nodes, statemachine, urischemes, utils
from docutils.transforms import universal
from docutils.parsers import rst
from docutils.parsers.rst import states, tableparser, directives, languages
from docutils.readers import standalone, pep, python
from docutils.readers.python import moduleparser
from docutils.statemachine import string2lines

try:
    import mypdb as pdb
except:
    import pdb


class DevNull:

    """Output sink."""

    def write(self, string):
        pass


class CustomTestSuite(unittest.TestSuite):

    """
    A collection of custom TestCases.

    """

    id = ''
    """Identifier for the TestSuite. Prepended to the
    TestCase identifiers to make identification easier."""

    next_test_case_id = 0
    """The next identifier to use for non-identified test cases."""

    def __init__(self, tests=(), id=None):
        """
        Initialize the CustomTestSuite.

        Arguments:

        id -- identifier for the suite, prepended to test cases.
        """
        unittest.TestSuite.__init__(self, tests)
        if id is None:
            mypath = os.path.abspath(
                sys.modules[CustomTestSuite.__module__].__file__)
            outerframes = inspect.getouterframes(inspect.currentframe())
            for outerframe in outerframes[1:]:
                if outerframe[3] != '__init__':
                    callerpath = outerframe[1]
                    if callerpath is None:
                        # It happens sometimes.  Why is a mystery.
                        callerpath = os.getcwd()
                    callerpath = os.path.abspath(callerpath)
                    break
            mydir, myname = os.path.split(mypath)
            if not mydir:
                mydir = os.curdir
            if callerpath.startswith(mydir):
                self.id = callerpath[len(mydir) + 1:] # caller's module
            else:
                self.id = callerpath
        else:
            self.id = id

    def addTestCase(self, test_case_class, method_name, input, expected,
                    id=None, run_in_debugger=0, short_description=None,
                    **kwargs):
        """
        Create a custom TestCase in the CustomTestSuite.
        Also return it, just in case.

        Arguments:

        test_case_class --
        method_name --
        input -- input to the parser.
        expected -- expected output from the parser.
        id -- unique test identifier, used by the test framework.
        run_in_debugger -- if true, run this test under the pdb debugger.
        short_description -- override to default test description.
        """
        if id is None:                  # generate id if required
            id = self.next_test_case_id
            self.next_test_case_id += 1
        # test identifier will become suiteid.testid
        tcid = '%s: %s' % (self.id, id)
        # generate and add test case
        tc = test_case_class(method_name, input, expected, tcid,
                             run_in_debugger=run_in_debugger,
                             short_description=short_description,
                             **kwargs)
        self.addTest(tc)
        return tc


class CustomTestCase(unittest.TestCase):

    compare = difflib.Differ().compare
    """Comparison method shared by all subclasses."""

    def __init__(self, method_name, input, expected, id,
                 run_in_debugger=0, short_description=None):
        """
        Initialise the CustomTestCase.

        Arguments:

        method_name -- name of test method to run.
        input -- input to the parser.
        expected -- expected output from the parser.
        id -- unique test identifier, used by the test framework.
        run_in_debugger -- if true, run this test under the pdb debugger.
        short_description -- override to default test description.
        """
        self.id = id
        self.input = input
        self.expected = expected
        self.run_in_debugger = run_in_debugger
        # Ring your mother.
        unittest.TestCase.__init__(self, method_name)

    def __str__(self):
        """
        Return string conversion. Overridden to give test id, in addition to
        method name.
        """
        return '%s; %s' % (self.id, unittest.TestCase.__str__(self))

    def __repr__(self):
        return "<%s %s>" % (self.id, unittest.TestCase.__repr__(self))

    def compare_output(self, input, output, expected):
        """`input`, `output`, and `expected` should all be strings."""
        if type(input) == UnicodeType:
            input = input.encode('raw_unicode_escape')
        if type(output) == UnicodeType:
            output = output.encode('raw_unicode_escape')
        if type(expected) == UnicodeType:
            expected = expected.encode('raw_unicode_escape')
        try:
            self.assertEquals('\n' + output, '\n' + expected)
        except AssertionError:
            print >>sys.stderr, '\n%s\ninput:' % (self,)
            print >>sys.stderr, input
            print >>sys.stderr, '-: expected\n+: output'
            print >>sys.stderr, ''.join(self.compare(expected.splitlines(1),
                                                     output.splitlines(1)))
            raise


class TransformTestSuite(CustomTestSuite):

    """
    A collection of TransformTestCases.

    A TransformTestSuite instance manufactures TransformTestCases,
    keeps track of them, and provides a shared test fixture (a-la
    setUp and tearDown).
    """

    def __init__(self, parser):
        self.parser = parser
        """Parser shared by all test cases."""

        CustomTestSuite.__init__(self)

    def generateTests(self, dict, dictname='totest',
                      testmethod='test_transforms'):
        """
        Stock the suite with test cases generated from a test data dictionary.

        Each dictionary key (test type's name) maps to a list of transform
        classes and list of tests. Each test is a list: input, expected
        output, optional modifier. The optional third entry, a behavior
        modifier, can be 0 (temporarily disable this test) or 1 (run this test
        under the pdb debugger). Tests should be self-documenting and not
        require external comments.
        """
        for name, (transforms, cases) in dict.items():
            for casenum in range(len(cases)):
                case = cases[casenum]
                run_in_debugger = 0
                if len(case)==3:
                    if case[2]:
                        run_in_debugger = 1
                    else:
                        continue
                self.addTestCase(
                      TransformTestCase, testmethod,
                      transforms=transforms, parser=self.parser,
                      input=case[0], expected=case[1],
                      id='%s[%r][%s]' % (dictname, name, casenum),
                      run_in_debugger=run_in_debugger)


class TransformTestCase(CustomTestCase):

    """
    Output checker for the transform.

    Should probably be called TransformOutputChecker, but I can deal with
    that later when/if someone comes up with a category of transform test
    cases that have nothing to do with the input and output of the transform.
    """

    option_parser = frontend.OptionParser(components=(rst.Parser,))
    settings = option_parser.get_default_values()
    settings.report_level = 1
    settings.halt_level = 5
    settings.debug = package_unittest.debug
    settings.warning_stream = DevNull()

    def __init__(self, *args, **kwargs):
        self.transforms = kwargs['transforms']
        """List of transforms to perform for this test case."""

        self.parser = kwargs['parser']
        """Input parser for this test case."""

        del kwargs['transforms'], kwargs['parser'] # only wanted here
        CustomTestCase.__init__(self, *args, **kwargs)

    def supports(self, format):
        return 1

    def test_transforms(self):
        if self.run_in_debugger:
            pdb.set_trace()
        document = utils.new_document('test data', self.settings)
        self.parser.parse(self.input, document)
        # Don't do a ``populate_from_components()`` because that would
        # enable the Transformer's default transforms.
        document.transformer.add_transforms(self.transforms)
        document.transformer.add_transform(universal.TestMessages)
        document.transformer.components['writer'] = self
        document.transformer.apply_transforms()
        output = document.pformat()
        self.compare_output(self.input, output, self.expected)

    def test_transforms_verbosely(self):
        if self.run_in_debugger:
            pdb.set_trace()
        print '\n', self.id
        print '-' * 70
        print self.input
        document = utils.new_document('test data', self.settings)
        self.parser.parse(self.input, document)
        print '-' * 70
        print document.pformat()
        for transformClass in self.transforms:
            transformClass(document).apply()
        output = document.pformat()
        print '-' * 70
        print output
        self.compare_output(self.input, output, self.expected)


class ParserTestCase(CustomTestCase):

    """
    Output checker for the parser.

    Should probably be called ParserOutputChecker, but I can deal with
    that later when/if someone comes up with a category of parser test
    cases that have nothing to do with the input and output of the parser.
    """

    parser = rst.Parser()
    """Parser shared by all ParserTestCases."""

    option_parser = frontend.OptionParser(components=(parser,))
    settings = option_parser.get_default_values()
    settings.report_level = 5
    settings.halt_level = 5
    settings.debug = package_unittest.debug

    def test_parser(self):
        if self.run_in_debugger:
            pdb.set_trace()
        document = utils.new_document('test data', self.settings)
        self.parser.parse(self.input, document)
        output = document.pformat()
        self.compare_output(self.input, output, self.expected)


class ParserTestSuite(CustomTestSuite):

    """
    A collection of ParserTestCases.

    A ParserTestSuite instance manufactures ParserTestCases,
    keeps track of them, and provides a shared test fixture (a-la
    setUp and tearDown).
    """

    test_case_class = ParserTestCase

    def generateTests(self, dict, dictname='totest'):
        """
        Stock the suite with test cases generated from a test data dictionary.

        Each dictionary key (test type name) maps to a list of tests. Each
        test is a list: input, expected output, optional modifier. The
        optional third entry, a behavior modifier, can be 0 (temporarily
        disable this test) or 1 (run this test under the pdb debugger). Tests
        should be self-documenting and not require external comments.
        """
        for name, cases in dict.items():
            for casenum in range(len(cases)):
                case = cases[casenum]
                run_in_debugger = 0
                if len(case)==3:
                    if case[2]:
                        run_in_debugger = 1
                    else:
                        continue
                self.addTestCase(
                      self.test_case_class, 'test_parser',
                      input=case[0], expected=case[1],
                      id='%s[%r][%s]' % (dictname, name, casenum),
                      run_in_debugger=run_in_debugger)


class PEPParserTestCase(ParserTestCase):

    """PEP-specific parser test case."""

    parser = rst.Parser(rfc2822=1, inliner=pep.Inliner())
    """Parser shared by all PEPParserTestCases."""

    option_parser = frontend.OptionParser(components=(parser, pep.Reader))
    settings = option_parser.get_default_values()
    settings.report_level = 5
    settings.halt_level = 5
    settings.debug = package_unittest.debug


class PEPParserTestSuite(ParserTestSuite):

    """A collection of PEPParserTestCases."""

    test_case_class = PEPParserTestCase


class GridTableParserTestCase(CustomTestCase):

    parser = tableparser.GridTableParser()

    def test_parse_table(self):
        self.parser.setup(string2lines(self.input))
        try:
            self.parser.find_head_body_sep()
            self.parser.parse_table()
            output = self.parser.cells
        except Exception, details:
            output = '%s: %s' % (details.__class__.__name__, details)
        self.compare_output(self.input, pformat(output) + '\n',
                            pformat(self.expected) + '\n')

    def test_parse(self):
        try:
            output = self.parser.parse(string2lines(self.input))
        except Exception, details:
            output = '%s: %s' % (details.__class__.__name__, details)
        self.compare_output(self.input, pformat(output) + '\n',
                            pformat(self.expected) + '\n')


class GridTableParserTestSuite(CustomTestSuite):

    """
    A collection of GridTableParserTestCases.

    A GridTableParserTestSuite instance manufactures GridTableParserTestCases,
    keeps track of them, and provides a shared test fixture (a-la setUp and
    tearDown).
    """

    test_case_class = GridTableParserTestCase

    def generateTests(self, dict, dictname='totest'):
        """
        Stock the suite with test cases generated from a test data dictionary.

        Each dictionary key (test type name) maps to a list of tests. Each
        test is a list: an input table, expected output from parse_table(),
        expected output from parse(), optional modifier. The optional fourth
        entry, a behavior modifier, can be 0 (temporarily disable this test)
        or 1 (run this test under the pdb debugger). Tests should be
        self-documenting and not require external comments.
        """
        for name, cases in dict.items():
            for casenum in range(len(cases)):
                case = cases[casenum]
                run_in_debugger = 0
                if len(case) == 4:
                    if case[-1]:
                        run_in_debugger = 1
                    else:
                        continue
                self.addTestCase(self.test_case_class, 'test_parse_table',
                                 input=case[0], expected=case[1],
                                 id='%s[%r][%s]' % (dictname, name, casenum),
                                 run_in_debugger=run_in_debugger)
                self.addTestCase(self.test_case_class, 'test_parse',
                                 input=case[0], expected=case[2],
                                 id='%s[%r][%s]' % (dictname, name, casenum),
                                 run_in_debugger=run_in_debugger)


class SimpleTableParserTestCase(GridTableParserTestCase):

    parser = tableparser.SimpleTableParser()


class SimpleTableParserTestSuite(CustomTestSuite):

    """
    A collection of SimpleTableParserTestCases.
    """

    test_case_class = SimpleTableParserTestCase

    def generateTests(self, dict, dictname='totest'):
        """
        Stock the suite with test cases generated from a test data dictionary.

        Each dictionary key (test type name) maps to a list of tests. Each
        test is a list: an input table, expected output from parse(), optional
        modifier. The optional third entry, a behavior modifier, can be 0
        (temporarily disable this test) or 1 (run this test under the pdb
        debugger). Tests should be self-documenting and not require external
        comments.
        """
        for name, cases in dict.items():
            for casenum in range(len(cases)):
                case = cases[casenum]
                run_in_debugger = 0
                if len(case) == 3:
                    if case[-1]:
                        run_in_debugger = 1
                    else:
                        continue
                self.addTestCase(self.test_case_class, 'test_parse',
                                 input=case[0], expected=case[1],
                                 id='%s[%r][%s]' % (dictname, name, casenum),
                                 run_in_debugger=run_in_debugger)


class PythonModuleParserTestSuite(CustomTestSuite):

    """
    A collection of PythonModuleParserTestCase.
    """

    def generateTests(self, dict, dictname='totest',
                      testmethod='test_parser'):
        """
        Stock the suite with test cases generated from a test data dictionary.

        Each dictionary key (test type's name) maps to a list of tests. Each
        test is a list: input, expected output, optional modifier. The
        optional third entry, a behavior modifier, can be 0 (temporarily
        disable this test) or 1 (run this test under the pdb debugger). Tests
        should be self-documenting and not require external comments.
        """
        for name, cases in dict.items():
            for casenum in range(len(cases)):
                case = cases[casenum]
                run_in_debugger = 0
                if len(case)==3:
                    if case[2]:
                        run_in_debugger = 1
                    else:
                        continue
                self.addTestCase(
                      PythonModuleParserTestCase, testmethod,
                      input=case[0], expected=case[1],
                      id='%s[%r][%s]' % (dictname, name, casenum),
                      run_in_debugger=run_in_debugger)


class PythonModuleParserTestCase(CustomTestCase):

    def test_parser(self):
        if self.run_in_debugger:
            pdb.set_trace()
        module = moduleparser.parse_module(self.input, 'test data')
        output = str(module)
        self.compare_output(self.input, output, self.expected)

    def test_token_parser_rhs(self): 
        if self.run_in_debugger:
            pdb.set_trace()
        tr = moduleparser.TokenParser(self.input)
        output = tr.rhs(1)
        self.compare_output(self.input, output, self.expected)


def exception_args(code):
    try:
        exec(code)
    except Exception, detail:
        return detail.args
