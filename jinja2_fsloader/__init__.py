# coding: utf-8
"""jinja2_fsloader - A Jinja2 template loader using PyFilesystem2.
"""

import fs
import fs.path
import fs.errors
import jinja2
import pkg_resources


__author__ = "Martin Larralde <martin.larralde@ens-paris-saclay.fr>"
__license__ = "MIT"
__version__ = pkg_resources.resource_string(__name__, "_version.txt").decode('utf-8').strip()


class FSLoader(jinja2.BaseLoader):
    """Loads template from a PyFilesystem2.

    The loader is created with a :class:`~fs.base.FS` instance, or a FS URL
    which is used to search for the templates::

    >>> zip_loader = FSLoader("zip:///path/to/my/templates.zip")
    >>> ftp_loader = FSLoader(fs.ftpfs.FTPFS("server.net"))

    Per default the template encoding is ``'utf-8'`` which can be changed
    by setting the `encoding` parameter to something else. The `syspath`
    parameter can be opted in to provide Jinja2 the system path to the query
    if it exist, otherwise it will only return the internal filesystem path.

    .. seealso:: the `PyFilesystem docs <https://docs.pyfilesystem.org/>`_.

    """

    def __init__(self, template_fs, encoding='utf-8', use_syspath=False):
        self.fs = fs.open_fs(template_fs)
        self.use_syspath = use_syspath
        self.encoding = encoding

    def get_source(self, environment, template):
        if not self.fs.isfile(template):
            raise jinja2.TemplateNotFound(template)
        try:
            mtime = self.fs.getdetails(template).modified
            reload = lambda: self.fs.getdetails(template).modified > mtime
        except fs.errors.MissingInfoNamespace:
            reload = lambda: True
        with self.fs.open(template, encoding=self.encoding) as f:
            source = f.read()
        if self.use_syspath:
            if self.fs.hassyspath(template):
                return source, self.fs.getsyspath(template), reload
            elif self.fs.hasurl(template):
                return source, self.fs.geturl(template), reload
        return source, template, reload

    def list_templates(self):
        found = set()
        for file in self.fs.walk.files():
            found.add(fs.path.relpath(file))
        return sorted(found)
