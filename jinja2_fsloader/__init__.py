# coding: utf-8
"""jinja2_fsloader - A Jinja2 template loader using PyFilesystem2.
"""

import fs
import sys
import uuid
import fs.path
import fs.errors
import jinja2
import pkg_resources
from jinja2._compat import string_types
from fs.multifs import MultiFS

__author__ = "Martin Larralde <martin.larralde@ens-paris-saclay.fr>"
__license__ = "MIT"
__version__ = pkg_resources.resource_string(__name__, "_version.txt").decode('utf-8').strip()
PY2 = sys.version_info[0] == 2


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

    def __init__(self, template_fs_list, encoding='utf-8', use_syspath=False):
        if isinstance(template_fs_list, string_types) or isinstance(template_fs_list, fs.base.FS):
            template_fs_list = [template_fs_list]
        self.filesystem = MultiFS()
        for template_fs in template_fs_list:
            if isinstance(template_fs, fs.base.FS):
                self.filesystem.add_fs(uuid.uuid4().hex, fs.open_fs(template_fs))
            else:
                self.filesystem.add_fs(template_fs, fs.open_fs(template_fs))
        self.use_syspath = use_syspath
        self.encoding = encoding

    def get_source(self, environment, template):
        template = to_unicode(template)
        for _, a_filesystem in self.filesystem.iterate_fs():
            try:
                return self._get_source(a_filesystem, template)
            except jinja2.TemplateNotFound:
                # try next file system
                continue
        # none of the file system has it
        raise jinja2.TemplateNotFound(template)

    def _get_source(self, filesystem, template):
        if not filesystem.isfile(template):
            raise jinja2.TemplateNotFound(template)
        try:
            mtime = filesystem.getdetails(template).modified
            reload = lambda: filesystem.getdetails(template).modified > mtime
        except fs.errors.MissingInfoNamespace:
            reload = lambda: True
        with filesystem.open(template, encoding=self.encoding) as input_file:
            source = input_file.read()
        if self.use_syspath:
            if filesystem.hassyspath(template):
                return source, filesystem.getsyspath(template), reload
            elif filesystem.hasurl(template):
                return source, filesystem.geturl(template), reload
        return source, template, reload

    def list_templates(self):
        found = set()
        for _, a_filesystem in self.filesystem.iterate_fs():
            for file in a_filesystem.walk.files():
                found.add(fs.path.relpath(file))
        return sorted(found)


def to_unicode(path):
    """Convert str in python 2 to unitcode"""
    if PY2 and path.__class__.__name__ != "unicode":
        return u"".__class__(path)
    return path
