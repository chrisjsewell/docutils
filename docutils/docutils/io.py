#! /usr/bin/env python

"""
:Author: David Goodger
:Contact: goodger@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

I/O classes provide a uniform API for low-level input and output.  Subclasses
will exist for a variety of input/output mechanisms.
"""

__docformat__ = 'reStructuredText'

import sys
import locale


class IO:

    """
    Base class for abstract input/output wrappers.
    """

    def __init__(self, options, source=None, source_path=None,
                 destination=None, destination_path=None):
        self.options = options
        """An option values object with "input_encoding" and "output_encoding"
        attributes (typically a `docutils.optik.Values` object)."""

        self.source = source
        """The source of input data."""

        self.source_path = source_path
        """A text reference to the source."""

        self.destination = destination
        """The destination for output data."""

        self.destination_path = destination_path
        """A text reference to the destination."""

    def __repr__(self):
        return '%s: source=%r, destination=%r' % (self.__class__, self.source,
                                                  self.destination)

    def read(self, reader):
        raise NotImplementedError

    def write(self, data):
        raise NotImplementedError

    def decode(self, data):
        """
        Decode a string, `data`, heuristically.
        Raise UnicodeError if unsuccessful.

        The client application should call ``locale.setlocale`` at the
        beginning of processing::

            locale.setlocale(locale.LC_ALL, '')
        """
        encodings = [self.options.input_encoding, 'utf-8']
        try:
            encodings.append(locale.nl_langinfo(locale.CODESET))
        except:
            pass
        try:
            encodings.append(locale.getlocale()[1])
        except:
            pass
        try:
            encodings.append(locale.getdefaultlocale()[1])
        except:
            pass
        encodings.append('latin-1')
        for enc in encodings:
            if not enc:
                continue
            try:
                decoded = unicode(data, enc)
                return decoded
            except (UnicodeError, LookupError):
                pass
        raise UnicodeError(
            'Unable to decode input data.  Tried the following encodings: %s.'
            % ', '.join([repr(enc) for enc in encodings if enc]))


class FileIO(IO):

    """
    I/O for single, simple file-like objects.
    """

    def __init__(self, options, source=None, source_path=None,
                 destination=None, destination_path=None):
        """
        :Parameters:
            - `source`: either a file-like object (which is read directly), or
              `None` (which implies `sys.stdin` if no `source_path` given).
            - `source_path`: a path to a file, which is opened and then read.
            - `destination`: either a file-like object (which is written
              directly) or `None` (which implies `sys.stdout` if no
              `destination_path` given).
            - `destination_path`: a path to a file, which is opened and then
              written.
        """
        IO.__init__(self, options, source, source_path, destination,
                    destination_path)
        if source is None:
            if source_path:
                self.source = open(source_path)
            else:
                self.source = sys.stdin
        if destination is None:
            if destination_path:
                self.destination = open(destination_path, 'w')
            else:
                self.destination = sys.stdout

    def read(self, reader):
        """Read and decode a single file and return the data."""
        data = self.source.read()
        return self.decode(data)

    def write(self, data):
        """Encode and write `data` to a single file."""
        output = data.encode(self.options.output_encoding)
        self.destination.write(output)


class StringIO(IO):

    """
    Direct string I/O.
    """

    def read(self, reader):
        """Decode and return the source string."""
        return self.decode(self.source)

    def write(self, data):
        """Encode and return `data`."""
        self.destination = data.encode(self.options.output_encoding)
        return self.destination


class NullIO(IO):

    """
    Degenerate I/O: read & write nothing.
    """

    def read(self, reader):
        """Return a null string."""
        return u''

    def write(self, data):
        """Do nothing (send data to the bit bucket)."""
        pass
