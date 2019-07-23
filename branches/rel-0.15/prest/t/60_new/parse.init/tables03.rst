Test Specifying Row and Entry Attributes
----------------------------------------

.. perl:: 
   $PARSER->{opt}{D}{'rowattr'}='valign="top"'; "";
   sub blue { $PARSER->{opt}{D}{'entryattr'} = 'bgcolor="blue"'; "" }
   sub red { $PARSER->{opt}{D}{'entryattr'} = 'bgcolor="red"'; "" }
   sub clear { delete $PARSER->{opt}{D}{'entryattr'}; "" }
   sub bottom { $PARSER->{opt}{D}{'rowattr'}='valign="bottom"'; "" }

=========== ============= ============= =============
..	      **Average**                **Comment**
----------- --------------------------- -------------
..	     **Height**    **Weight**   .. perl::
                                           clear();
             .. perl::    .. perl::
                blue();      red();
=========== ============= ============= =============
**males**              11         0.003 stronger
**females**             9         0.002 *smarter*
=========== ============= ============= =============

+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | Cells may span columns.          |
|                        |                                  |
| .. perl:: blue();      | .. perl:: red();                 |
+------------------------+------------+---------------------+
| body row 3             | Cells may  | - Table cells       |
|                        | span rows. | - contain           |
| .. perl:: bottom();    |            | - body elements.    |
| .. perl:: clear();     |            |                     |
+------------------------+            |                     |
| body row 4             |            |                     |
+------------------------+------------+---------------------+
