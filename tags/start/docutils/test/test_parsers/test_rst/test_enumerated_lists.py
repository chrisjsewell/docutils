#! /usr/bin/env python

"""
:Author: David Goodger
:Contact: goodger@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

Tests for states.py.
"""

import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['enumerated_lists'] = [
["""\
1. Item one.

2. Item two.

3. Item three.
""",
"""\
<document>
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one.
        <list_item>
            <paragraph>
                Item two.
        <list_item>
            <paragraph>
                Item three.
"""],
["""\
No blank lines betwen items:

1. Item one.
2. Item two.
3. Item three.
""",
"""\
<document>
    <paragraph>
        No blank lines betwen items:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one.
        <list_item>
            <paragraph>
                Item two.
        <list_item>
            <paragraph>
                Item three.
"""],
["""\
1.
empty item above, no blank line
""",
"""\
<document>
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
    <system_message level="2" type="WARNING">
        <paragraph>
            Unindent without blank line at line 2.
    <paragraph>
        empty item above, no blank line
"""],
["""\
Scrambled:

3. Item three.
2. Item two.
1. Item one.
""",
"""\
<document>
    <paragraph>
        Scrambled:
    <system_message level="1" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1 at line 3: '3' (ordinal 3)
    <enumerated_list enumtype="arabic" prefix="" start="3" suffix=".">
        <list_item>
            <paragraph>
                Item three.
    <system_message level="2" type="WARNING">
        <paragraph>
            Unindent without blank line at line 4.
    <system_message level="1" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1 at line 4: '2' (ordinal 2)
    <enumerated_list enumtype="arabic" prefix="" start="2" suffix=".">
        <list_item>
            <paragraph>
                Item two.
    <system_message level="2" type="WARNING">
        <paragraph>
            Unindent without blank line at line 5.
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one.
"""],
["""\
Skipping item 3:

1. Item 1.
2. Item 2.
4. Item 4.
""",
"""\
<document>
    <paragraph>
        Skipping item 3:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item 1.
        <list_item>
            <paragraph>
                Item 2.
    <system_message level="2" type="WARNING">
        <paragraph>
            Unindent without blank line at line 4.
    <system_message level="1" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1 at line 5: '4' (ordinal 4)
    <enumerated_list enumtype="arabic" prefix="" start="4" suffix=".">
        <list_item>
            <paragraph>
                Item 4.
"""],
["""\
Start with non-ordinal-1:

0. Item zero.
1. Item one.
2. Item two.
3. Item three.

And again:

2. Item two.
3. Item three.
""",
"""\
<document>
    <paragraph>
        Start with non-ordinal-1:
    <system_message level="1" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1 at line 3: '0' (ordinal 0)
    <enumerated_list enumtype="arabic" prefix="" start="0" suffix=".">
        <list_item>
            <paragraph>
                Item zero.
        <list_item>
            <paragraph>
                Item one.
        <list_item>
            <paragraph>
                Item two.
        <list_item>
            <paragraph>
                Item three.
    <paragraph>
        And again:
    <system_message level="1" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1 at line 10: '2' (ordinal 2)
    <enumerated_list enumtype="arabic" prefix="" start="2" suffix=".">
        <list_item>
            <paragraph>
                Item two.
        <list_item>
            <paragraph>
                Item three.
"""],
["""\
1. Item one: line 1,
   line 2.
2. Item two: line 1,
   line 2.
3. Item three: paragraph 1, line 1,
   line 2.

   Paragraph 2.
""",
"""\
<document>
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item one: line 1,
                line 2.
        <list_item>
            <paragraph>
                Item two: line 1,
                line 2.
        <list_item>
            <paragraph>
                Item three: paragraph 1, line 1,
                line 2.
            <paragraph>
                Paragraph 2.
"""],
["""\
Different enumeration sequences:

1. Item 1.
2. Item 2.
3. Item 3.

A. Item A.
B. Item B.
C. Item C.

a. Item a.
b. Item b.
c. Item c.

I. Item I.
II. Item II.
III. Item III.

i. Item i.
ii. Item ii.
iii. Item iii.
""",
"""\
<document>
    <paragraph>
        Different enumeration sequences:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item 1.
        <list_item>
            <paragraph>
                Item 2.
        <list_item>
            <paragraph>
                Item 3.
    <enumerated_list enumtype="upperalpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item A.
        <list_item>
            <paragraph>
                Item B.
        <list_item>
            <paragraph>
                Item C.
    <enumerated_list enumtype="loweralpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item a.
        <list_item>
            <paragraph>
                Item b.
        <list_item>
            <paragraph>
                Item c.
    <enumerated_list enumtype="upperroman" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item I.
        <list_item>
            <paragraph>
                Item II.
        <list_item>
            <paragraph>
                Item III.
    <enumerated_list enumtype="lowerroman" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item i.
        <list_item>
            <paragraph>
                Item ii.
        <list_item>
            <paragraph>
                Item iii.
"""],
["""\
Bad Roman numerals:

i. i
ii. ii
iii. iii
iiii. iiii

(I) I
(IVXLCDM) IVXLCDM
""",
"""\
<document>
    <paragraph>
        Bad Roman numerals:
    <enumerated_list enumtype="lowerroman" prefix="" suffix=".">
        <list_item>
            <paragraph>
                i
        <list_item>
            <paragraph>
                ii
        <list_item>
            <paragraph>
                iii
    <system_message level="2" type="WARNING">
        <paragraph>
            Unindent without blank line at line 4.
    <system_message level="3" type="ERROR">
        <paragraph>
            Enumerated list start value invalid at line 6: 'iiii' (sequence 'lowerroman')
    <block_quote>
        <paragraph>
            iiii
    <enumerated_list enumtype="upperroman" prefix="(" suffix=")">
        <list_item>
            <paragraph>
                I
    <system_message level="2" type="WARNING">
        <paragraph>
            Unindent without blank line at line 9.
    <system_message level="3" type="ERROR">
        <paragraph>
            Enumerated list start value invalid at line 9: 'IVXLCDM' (sequence 'upperroman')
    <block_quote>
        <paragraph>
            IVXLCDM
"""],
["""\
Potentially ambiguous cases:

A. Item A.
B. Item B.
C. Item C.

I. Item I.
II. Item II.
III. Item III.

a. Item a.
b. Item b.
c. Item c.

i. Item i.
ii. Item ii.
iii. Item iii.

Phew! Safe!
""",
"""\
<document>
    <paragraph>
        Potentially ambiguous cases:
    <enumerated_list enumtype="upperalpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item A.
        <list_item>
            <paragraph>
                Item B.
        <list_item>
            <paragraph>
                Item C.
    <enumerated_list enumtype="upperroman" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item I.
        <list_item>
            <paragraph>
                Item II.
        <list_item>
            <paragraph>
                Item III.
    <enumerated_list enumtype="loweralpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item a.
        <list_item>
            <paragraph>
                Item b.
        <list_item>
            <paragraph>
                Item c.
    <enumerated_list enumtype="lowerroman" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item i.
        <list_item>
            <paragraph>
                Item ii.
        <list_item>
            <paragraph>
                Item iii.
    <paragraph>
        Phew! Safe!
"""],
["""\
Definitely ambiguous:

A. Item A.
B. Item B.
C. Item C.
D. Item D.
E. Item E.
F. Item F.
G. Item G.
H. Item H.
I. Item I.
II. Item II.
III. Item III.

a. Item a.
b. Item b.
c. Item c.
d. Item d.
e. Item e.
f. Item f.
g. Item g.
h. Item h.
i. Item i.
ii. Item ii.
iii. Item iii.
""",
"""\
<document>
    <paragraph>
        Definitely ambiguous:
    <enumerated_list enumtype="upperalpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item A.
        <list_item>
            <paragraph>
                Item B.
        <list_item>
            <paragraph>
                Item C.
        <list_item>
            <paragraph>
                Item D.
        <list_item>
            <paragraph>
                Item E.
        <list_item>
            <paragraph>
                Item F.
        <list_item>
            <paragraph>
                Item G.
        <list_item>
            <paragraph>
                Item H.
        <list_item>
            <paragraph>
                Item I.
    <system_message level="2" type="WARNING">
        <paragraph>
            Unindent without blank line at line 4.
    <system_message level="1" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1 at line 12: 'II' (ordinal 2)
    <enumerated_list enumtype="upperroman" prefix="" start="2" suffix=".">
        <list_item>
            <paragraph>
                Item II.
        <list_item>
            <paragraph>
                Item III.
    <enumerated_list enumtype="loweralpha" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item a.
        <list_item>
            <paragraph>
                Item b.
        <list_item>
            <paragraph>
                Item c.
        <list_item>
            <paragraph>
                Item d.
        <list_item>
            <paragraph>
                Item e.
        <list_item>
            <paragraph>
                Item f.
        <list_item>
            <paragraph>
                Item g.
        <list_item>
            <paragraph>
                Item h.
        <list_item>
            <paragraph>
                Item i.
    <system_message level="2" type="WARNING">
        <paragraph>
            Unindent without blank line at line 16.
    <system_message level="1" type="INFO">
        <paragraph>
            Enumerated list start value not ordinal-1 at line 24: 'ii' (ordinal 2)
    <enumerated_list enumtype="lowerroman" prefix="" start="2" suffix=".">
        <list_item>
            <paragraph>
                Item ii.
        <list_item>
            <paragraph>
                Item iii.
"""],
["""\
Different enumeration formats:

1. Item 1.
2. Item 2.
3. Item 3.

1) Item 1).
2) Item 2).
3) Item 3).

(1) Item (1).
(2) Item (2).
(3) Item (3).
""",
"""\
<document>
    <paragraph>
        Different enumeration formats:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item 1.
        <list_item>
            <paragraph>
                Item 2.
        <list_item>
            <paragraph>
                Item 3.
    <enumerated_list enumtype="arabic" prefix="" suffix=")">
        <list_item>
            <paragraph>
                Item 1).
        <list_item>
            <paragraph>
                Item 2).
        <list_item>
            <paragraph>
                Item 3).
    <enumerated_list enumtype="arabic" prefix="(" suffix=")">
        <list_item>
            <paragraph>
                Item (1).
        <list_item>
            <paragraph>
                Item (2).
        <list_item>
            <paragraph>
                Item (3).
"""],
["""\
Nested enumerated lists:

1. Item 1.

   A) Item A).
   B) Item B).
   C) Item C).

2. Item 2.

   (a) Item (a).

       I) Item I).
       II) Item II).
       III) Item III).

   (b) Item (b).

   (c) Item (c).

       (i) Item (i).
       (ii) Item (ii).
       (iii) Item (iii).

3. Item 3.
""",
"""\
<document>
    <paragraph>
        Nested enumerated lists:
    <enumerated_list enumtype="arabic" prefix="" suffix=".">
        <list_item>
            <paragraph>
                Item 1.
            <enumerated_list enumtype="upperalpha" prefix="" suffix=")">
                <list_item>
                    <paragraph>
                        Item A).
                <list_item>
                    <paragraph>
                        Item B).
                <list_item>
                    <paragraph>
                        Item C).
        <list_item>
            <paragraph>
                Item 2.
            <enumerated_list enumtype="loweralpha" prefix="(" suffix=")">
                <list_item>
                    <paragraph>
                        Item (a).
                    <enumerated_list enumtype="upperroman" prefix="" suffix=")">
                        <list_item>
                            <paragraph>
                                Item I).
                        <list_item>
                            <paragraph>
                                Item II).
                        <list_item>
                            <paragraph>
                                Item III).
                <list_item>
                    <paragraph>
                        Item (b).
                <list_item>
                    <paragraph>
                        Item (c).
                    <enumerated_list enumtype="lowerroman" prefix="(" suffix=")">
                        <list_item>
                            <paragraph>
                                Item (i).
                        <list_item>
                            <paragraph>
                                Item (ii).
                        <list_item>
                            <paragraph>
                                Item (iii).
        <list_item>
            <paragraph>
                Item 3.
"""],
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
