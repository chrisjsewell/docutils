#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Author: David Goodger
# Contact: goodger@python.org
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Tests for tables.py directives.
"""

from __init__ import DocutilsTestSupport

try:
    import csv
except ImportError:
    csv = None


def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['table'] = [
["""\
.. table:: Truth table for "not"
   :class: custom

   =====  =====
     A    not A
   =====  =====
   False  True
   True   False
   =====  =====
""",
"""\
<document source="test data">
    <table class="custom">
        <title>
            Truth table for "not"
        <tgroup cols="2">
            <colspec colwidth="5">
            <colspec colwidth="5">
            <thead>
                <row>
                    <entry>
                        <paragraph>
                            A
                    <entry>
                        <paragraph>
                            not A
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            False
                    <entry>
                        <paragraph>
                            True
                <row>
                    <entry>
                        <paragraph>
                            True
                    <entry>
                        <paragraph>
                            False
"""],
["""\
.. table:: title with an *error

   ======  =====
   Simple  table
   ======  =====
""",
"""\
<document source="test data">
    <table>
        <title>
            title with an \n\
            <problematic id="id2" refid="id1">
                *
            error
        <tgroup cols="2">
            <colspec colwidth="6">
            <colspec colwidth="5">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            Simple
                    <entry>
                        <paragraph>
                            table
    <system_message backrefs="id2" id="id1" level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Inline emphasis start-string without end-string.
"""],
]

if csv:
    totest['csv-table'] = [
["""\
.. csv-table:: inline with integral header
   :widths: 10, 20, 30
   :header-rows: 1

   "Treat", "Quantity", "Description"
   "Albatross", 2.99, "On a stick!"
   "Crunchy Frog", 1.49, "If we took the bones out, it wouldn\'t be
   crunchy, now would it?"
   "Gannet Ripple", 1.99, "On a stick!"
""",
"""\
<document source="test data">
    <table>
        <title>
            inline with integral header
        <tgroup cols="3">
            <colspec colwidth="10">
            <colspec colwidth="20">
            <colspec colwidth="30">
            <thead>
                <row>
                    <entry>
                        <paragraph>
                            Treat
                    <entry>
                        <paragraph>
                            Quantity
                    <entry>
                        <paragraph>
                            Description
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            Albatross
                    <entry>
                        <paragraph>
                            2.99
                    <entry>
                        <paragraph>
                            On a stick!
                <row>
                    <entry>
                        <paragraph>
                            Crunchy Frog
                    <entry>
                        <paragraph>
                            1.49
                    <entry>
                        <paragraph>
                            If we took the bones out, it wouldn't be
                            crunchy, now would it?
                <row>
                    <entry>
                        <paragraph>
                            Gannet Ripple
                    <entry>
                        <paragraph>
                            1.99
                    <entry>
                        <paragraph>
                            On a stick!
"""],
["""\
.. csv-table:: inline with separate header
   :header: "Treat", Quantity, "Description"
   :widths: 10,20,30

   "Albatross", 2.99, "On a stick!"
""",
"""\
<document source="test data">
    <table>
        <title>
            inline with separate header
        <tgroup cols="3">
            <colspec colwidth="10">
            <colspec colwidth="20">
            <colspec colwidth="30">
            <thead>
                <row>
                    <entry>
                        <paragraph>
                            Treat
                    <entry>
                        <paragraph>
                            Quantity
                    <entry>
                        <paragraph>
                            Description
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            Albatross
                    <entry>
                        <paragraph>
                            2.99
                    <entry>
                        <paragraph>
                            On a stick!
"""],
["""\
.. csv-table:: complex internal structure
   :header: "Treat", Quantity, "
            * Description,
            * Definition, or
            * Narrative"

   "
   * Ice cream
   * Sorbet
   * Albatross", 2.99, "On a stick!"
""",
"""\
<document source="test data">
    <table>
        <title>
            complex internal structure
        <tgroup cols="3">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <thead>
                <row>
                    <entry>
                        <paragraph>
                            Treat
                    <entry>
                        <paragraph>
                            Quantity
                    <entry>
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Description,
                            <list_item>
                                <paragraph>
                                    Definition, or
                            <list_item>
                                <paragraph>
                                    Narrative
            <tbody>
                <row>
                    <entry>
                        <bullet_list bullet="*">
                            <list_item>
                                <paragraph>
                                    Ice cream
                            <list_item>
                                <paragraph>
                                    Sorbet
                            <list_item>
                                <paragraph>
                                    Albatross
                    <entry>
                        <paragraph>
                            2.99
                    <entry>
                        <paragraph>
                            On a stick!
"""],
["""\
.. csv-table:: short rows

   one, 2, three
   4, five
""",
"""\
<document source="test data">
    <table>
        <title>
            short rows
        <tgroup cols="3">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            one
                    <entry>
                        <paragraph>
                            2
                    <entry>
                        <paragraph>
                            three
                <row>
                    <entry>
                        <paragraph>
                            4
                    <entry>
                        <paragraph>
                            five
                    <entry>
"""],
["""\
.. csv-table:: short rows
   :header-rows: 1

   header col 1, header col 2
   one, 2, three
   4
""",
"""\
<document source="test data">
    <table>
        <title>
            short rows
        <tgroup cols="3">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <thead>
                <row>
                    <entry>
                        <paragraph>
                            header col 1
                    <entry>
                        <paragraph>
                            header col 2
                    <entry>
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            one
                    <entry>
                        <paragraph>
                            2
                    <entry>
                        <paragraph>
                            three
                <row>
                    <entry>
                        <paragraph>
                            4
                    <entry>
                    <entry>
"""],
[u"""\
.. csv-table:: non-ASCII characters

   Heiz\xf6lr\xfccksto\xdfabd\xe4mpfung
""",
u"""\
<document source="test data">
    <table>
        <title>
            non-ASCII characters
        <tgroup cols="1">
            <colspec colwidth="100">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            Heiz\xf6lr\xfccksto\xdfabd\xe4mpfung
"""],
["""\
.. csv-table:: empty
""",
"""\
<document source="test data">
    <system_message level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            The "csv-table" directive requires content; none supplied.
        <literal_block xml:space="preserve">
            .. csv-table:: empty
"""],
["""\
.. csv-table:: insufficient header row data
   :header-rows: 2

   some, csv, data
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            2 header row(s) specified but only 1 row(s) of data supplied ("csv-table" directive).
        <literal_block xml:space="preserve">
            .. csv-table:: insufficient header row data
               :header-rows: 2
            
               some, csv, data
"""],
["""\
.. csv-table:: insufficient body data
   :header-rows: 1

   some, csv, data
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Insufficient data supplied (1 row(s)); no data remaining for table body, required by "csv-table" directive.
        <literal_block xml:space="preserve">
            .. csv-table:: insufficient body data
               :header-rows: 1
            
               some, csv, data
"""],
["""\
.. csv-table:: content and external
   :file: bogus.csv

   some, csv, data
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            "csv-table" directive may not both specify an external file and have content.
        <literal_block xml:space="preserve">
            .. csv-table:: content and external
               :file: bogus.csv
            
               some, csv, data
"""],
["""\
.. csv-table:: external file and url
   :file: bogus.csv
   :url: http://example.org/bogus.csv
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            The "file" and "url" options may not be simultaneously specified for the "csv-table" directive.
        <literal_block xml:space="preserve">
            .. csv-table:: external file and url
               :file: bogus.csv
               :url: http://example.org/bogus.csv
"""],
["""\
.. csv-table:: error in the *title

   some, csv, data
""",
"""\
<document source="test data">
    <table>
        <title>
            error in the 
            <problematic id="id2" refid="id1">
                *
            title
        <tgroup cols="3">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            some
                    <entry>
                        <paragraph>
                            csv
                    <entry>
                        <paragraph>
                            data
    <system_message backrefs="id2" id="id1" level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Inline emphasis start-string without end-string.
"""],
["""\
.. csv-table:: no such file
   :file: bogus.csv
""",
"""\
<document source="test data">
    <system_message level="4" line="1" source="test data" type="SEVERE">
        <paragraph>
            Problems with "csv-table" directive path:
            [Errno 2] No such file or directory: 'bogus.csv'.
        <literal_block xml:space="preserve">
            .. csv-table:: no such file
               :file: bogus.csv
"""],
["""\
.. csv-table:: bad URL
   :url: bogus.csv
""",
"""\
<document source="test data">
    <system_message level="4" line="1" source="test data" type="SEVERE">
        <paragraph>
            Problems with "csv-table" directive URL "bogus.csv":
            unknown url type: bogus.csv.
        <literal_block xml:space="preserve">
            .. csv-table:: bad URL
               :url: bogus.csv
"""],
["""\
.. csv-table:: column mismatch
   :widths: 10,20

   some, csv, data
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            "csv-table" widths do not match the number of columns in table (3).
        <literal_block xml:space="preserve">
            .. csv-table:: column mismatch
               :widths: 10,20
            
               some, csv, data
"""],
["""\
.. csv-table:: bad column widths
   :widths: 10,y,z

   some, csv, data

.. csv-table:: bad column widths
   :widths: 0 0 0

   some, csv, data
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "csv-table" directive:
            invalid option value: (option: "widths"; value: '10,y,z')
            invalid literal for int(): y.
        <literal_block xml:space="preserve">
            .. csv-table:: bad column widths
               :widths: 10,y,z
            
               some, csv, data
    <system_message level="3" line="6" source="test data" type="ERROR">
        <paragraph>
            Error in "csv-table" directive:
            invalid option value: (option: "widths"; value: '0 0 0')
            negative or zero value; must be positive.
        <literal_block xml:space="preserve">
            .. csv-table:: bad column widths
               :widths: 0 0 0
            
               some, csv, data
"""],
["""\
.. csv-table:: good delimiter
   :delim: /

   some/csv/data

.. csv-table:: good delimiter
   :delim: \\

   some\\csv\\data

.. csv-table:: good delimiter
   :delim: 0x5c

   some\\csv\\data

.. csv-table:: good delimiter
   :delim: space

   some csv data
""",
"""\
<document source="test data">
    <table>
        <title>
            good delimiter
        <tgroup cols="3">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            some
                    <entry>
                        <paragraph>
                            csv
                    <entry>
                        <paragraph>
                            data
    <table>
        <title>
            good delimiter
        <tgroup cols="3">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            some
                    <entry>
                        <paragraph>
                            csv
                    <entry>
                        <paragraph>
                            data
    <table>
        <title>
            good delimiter
        <tgroup cols="3">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            some
                    <entry>
                        <paragraph>
                            csv
                    <entry>
                        <paragraph>
                            data
    <table>
        <title>
            good delimiter
        <tgroup cols="3">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <colspec colwidth="33">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            some
                    <entry>
                        <paragraph>
                            csv
                    <entry>
                        <paragraph>
                            data
"""],
["""\
.. csv-table:: bad delimiter
   :delim: multiple

.. csv-table:: bad delimiter
   :delim: U+9999999999999
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "csv-table" directive:
            invalid option value: (option: "delim"; value: 'multiple')
            'multiple' invalid; must be a single character or a Unicode code.
        <literal_block xml:space="preserve">
            .. csv-table:: bad delimiter
               :delim: multiple
    <system_message level="3" line="4" source="test data" type="ERROR">
        <paragraph>
            Error in "csv-table" directive:
            invalid option value: (option: "delim"; value: 'U+9999999999999')
            code too large (long int too large to convert to int).
        <literal_block xml:space="preserve">
            .. csv-table:: bad delimiter
               :delim: U+9999999999999
"""],
["""\
.. csv-table:: bad CSV data

   "bad", \"csv, data
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error with CSV data in "csv-table" directive:
            newline inside string
        <literal_block xml:space="preserve">
            .. csv-table:: bad CSV data
            
               "bad", \"csv, data
"""],
["""\
.. csv-table:: bad CSV header data
   :header: "bad", \"csv, data

   good, csv, data
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error with CSV data in "csv-table" directive:
            newline inside string
        <literal_block xml:space="preserve">
            .. csv-table:: bad CSV header data
               :header: "bad", \"csv, data
            
               good, csv, data
"""],
]
else:
    print ('Tests of "csv-table" directive skipped; '
           'Python 2.3 or higher required.')


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
