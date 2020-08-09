# docutils migration

[![codecov](https://codecov.io/gh/chrisjsewell/docutils/branch/develop/graph/badge.svg)](https://codecov.io/gh/chrisjsewell/docutils)

This package is a migration of docutils from <https://sourceforge.net/projects/docutils/> to GitHub.

It originates as a response to discussion in:

- https://sourceforge.net/p/docutils/feature-requests/58/
- https://sourceforge.net/p/docutils/mailman/message/37077728/
- https://github.com/sphinx-doc/sphinx/issues/8039

One of the reasons that appeared to come up is that it is too difficult and/or time consuming to migrate.
This package therefore shows how this can be done in a very simple, autonomous manner:

- migrating code, commit history (with authors) and branches using the [GitHub Importer](https://docs.github.com/en/github/importing-your-projects-to-github/about-github-importer) (this takes about 10 minutes),
- migrating tickets to issues using a python script that interfaces with the SourceForge and GitHub REST APIs (this is both autonomous and idempotent and takes about 10 minutes).

The `main` branch derives from the svn trunk, then here on the `develop` branch this README has been added and a GitHub workflow for Continuous Integration.

Note, two other migrations exist:

- https://github.com/docutils/docutils and https://github.com/docutils-mirror/docutils: these migrations are both from 2015 and do not include branches or ticket migration.
- https://github.com/live-clones/docutils/tree/master/docutils: this is a continually updated clone, but does not include branches, links to commit authors, or the ticket migration.
