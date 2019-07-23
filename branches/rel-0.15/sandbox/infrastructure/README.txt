==========================
 Docutils_ Infrastructure
==========================

:Author: Lea Wiemann
:Contact: grubert@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This document has been placed in the public domain.


The `infrastructure <.>`_ sandbox directory stores any scripts that
are needed for the development of the Docutils project.

:`<docutils-update.local>`_: The script to update the `web site`_
    from a developer machine or on shell.sourceforge.

    If a file ``ON_SOURCEFORGE`` exists in current dorectory, the
    script assumes being executed on shell.sourceforge.

:`<release.sh>`_: The script to make releases_ of Docutils.
    For usage details see `<release.txt>`_

    TODO : test. 
      Allow release without testing, because tests must be done
      on more than one os.

:`<release-test.sh>`_: The script to run tests at release time, extracted
    from ``release.sh``.

Everything below this line needs rework
---------------------------------------

Overview:

:`<uploaddocutils.sh>`_: Upload files to http://docutils.sf.net/tmp/
    using ``scp``, inserting the current date in the file name.

:`<update-htmlfiles>`_: Used to initialise a docutils-update upload directory.
    Generating html-files from txt-files first time.

:`<htmlfiles.lst>`_: The list of files for ``update-htmlfiles``.

and are these used by anyone.

:`<dbackport.sh>`_: Back-port changes from the trunk to the
    maintenance branch.

:`<fsfsbackup.sh>`_: Backup (mirror) an FSFS Subversion repository via
    SSH.  Used to backup the `Docutils Subversion repository`_.

.. _Docutils: http://docutils.sourceforge.net/
.. _Docutils check-in mailing list:
   http://docutils.sf.net/docs/user/mailing-lists.html#docutils-checkins
.. _web site: http://docutils.sourceforge.net/docs/dev/website.html
.. _Docutils Subversion repository:
   http://docutils.sourceforge.net/docs/dev/repository.html
.. _release.txt: http://docutils.sourceforge.net/docs/dev/release.html
