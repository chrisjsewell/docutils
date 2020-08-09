# docutils migration

This package is a migration of docutils from <https://sourceforge.net/projects/docutils/> ti GitHub.

It originates as a response to discussion in:

- https://sourceforge.net/p/docutils/feature-requests/58/
- https://sourceforge.net/p/docutils/mailman/message/37077728/
- https://github.com/sphinx-doc/sphinx/issues/8039

One of the reasons that appeared to come up is that it is too difficult and/or time consuming to migrate.
This package therefore shows how this can be done in a very simple, autonomous manner:
migrating code, commit history (with authors) and branches using the [GitHub Importer](https://docs.github.com/en/github/importing-your-projects-to-github/about-github-importer) (this takes about 10 minutes),
then migrating tickets to issues using a python script that interfaces with the SourceForge and GitHub REST APIs (this is both autonomous and idempotent and takes about 10 minutes).
