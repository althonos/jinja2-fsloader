# coding: utf-8
"""jinja2_fsloader - A Jinja2 template loader using PyFilesystem2.
"""

import fs
import fs.path
import fs.errors
import jinja2
import pkg_resources
from jinja2._compat import string_types

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

    def __init__(self, template_fs_list, encoding='utf-8', use_syspath=False):
        if isinstance(template_fs_list, string_types):
            template_fs_list = [template_fs_list]
        self.template_fs_list = template_fs_list
        self.use_syspath = use_syspath
        self.encoding = encoding

    def get_source(self, environment, template):
        for template_fs in self.template_fs_list:
            with fs.open_fs(template_fs) as fs_handle:
                if not fs.isfile(template):
                    continue
                try:
                    mtime = fs.getdetails(template).modified
                    reload = lambda: fs_handle.getdetails(template).modified > mtime
                except fs.errors.MissingInfoNamespace:
                    reload = lambda: True
                with fs.open(template, encoding=self.encoding) as f:
                    source = f.read()
                if self.use_syspath:
                    if fs.hassyspath(template):
                        return source, fs_handle.getsyspath(template), reload
                    elif fs.hasurl(template):
                        return source, fs_handle.geturl(template), reload
                return source, template, reload
        else:
            raise jinja2.TemplateNotFound(template)

    def list_templates(self):
        found = set()
        for template_fs in self.template_fs_list:
            with fs.open_fs(template_fs) as fs_handle:
                for file in fs_handle.walk.files():
                    found.add(fs.path.relpath(file))
        return sorted(found)
