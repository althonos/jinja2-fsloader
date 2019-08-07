``jinja2-fsloader``
===================

*A Jinja2 template loader using PyFilesystem2.*

|build| |repo| |versions| |changelog| |format| |coverage| |grade| |license|

.. |build| image:: https://img.shields.io/travis/althonos/jinja2-fsloader/master.svg?label=travis-ci&style=flat-square
   :target: https://travis-ci.org/althonos/jinja2-fsloader/

.. |repo| image:: https://img.shields.io/badge/source-GitHub-303030.svg?style=flat-square
   :target: https://github.com/althonos/jinja2-fsloader

.. |versions| image:: https://img.shields.io/pypi/v/jinja2-fsloader.svg?style=flat-square
   :target: https://pypi.org/project/jinja2-fsloader

.. |format| image:: https://img.shields.io/pypi/format/jinja2-fsloader.svg?style=flat-square
   :target: https://pypi.org/project/jinja2-fsloader

.. |grade| image:: https://img.shields.io/codacy/grade/f74bd301468341f59ce664ae129021ef/master.svg?style=flat-square
   :target: https://www.codacy.com/app/althonos/jinja2-fsloader/dashboard

.. |coverage| image:: https://img.shields.io/codecov/c/github/althonos/jinja2-fsloader/master.svg?style=flat-square
   :target: https://codecov.io/gh/althonos/jinja2-fsloader

.. |license| image:: https://img.shields.io/pypi/l/jinja2-fsloader.svg?style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |changelog| image:: https://img.shields.io/badge/keep%20a-changelog-8A0707.svg?maxAge=86400&style=flat-square
   :target: https://github.com/althonos/jinja2-fsloader/blob/master/CHANGELOG.rst

About
'''''

This library allows you to use PyFilesystem2 as a backend to load templates into
Jinja2. You can take advantage of the whole ``fs`` ecosystem, which already implements
drivers for FTP, SSH, SMB, S3, WebDAV servers, ZIP and Tar archives, and
`many more <https://www.pyfilesystem.org/page/index-of-filesystems/>`_!


Installation
''''''''''''

Install with ``pip``::

    $ pip install --user -U jinja2-fsloader


Usage
'''''

.. code:: Python

    from jinja2_fsloader import FSLoader
    FSLoader(template_fs, encoding='utf-8', use_syspath=False)

``template_fs``
    a ``FS`` instance or an `FS URL <https://docs.pyfilesystem.org/en/latest/openers.html>`_
    where the templates are located.
``encoding``
    the encoding of the template files (*utf-8* by default).
``use_syspath``
    set to ``True`` for the loader to return the real path or an URL to the template
    when available (``False`` by default).


Examples
''''''''

.. code:: python

    import jinja2
    from jinja2_fsloader import FSLoader

    # templates in a ZIP archive
    env = jinja2.Environment(loader=FSLoader("zip:///path/to/my/templates.zip"))

    # templates in a S3 bucket
    env = jinja.Environment(loader=FSLoader("s3://mybucket"))

    # templates in memory
    mem = fs.open_fs('mem://')
    mem.settext('template.j2', 'This template is {{adjective}}')
    env = jinja.Environment(loader=FSLoader(mem))


See Also
''''''''

The `complete documentation <https://www.pyfilesystem.org/>`_ of PyFilesystem2 can
give you a better overview of all the features available in the library.
