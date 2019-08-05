# coding: utf-8
from __future__ import unicode_literals

import unittest
import os

import fs
from fs.multifs import MultiFS
import jinja2

from jinja2_fsloader import FSLoader
from .utils import in_context


class TestFSLoader(unittest.TestCase):

    @staticmethod
    def build_env(filesystem, *args, **kwargs):
        return jinja2.Environment(
            loader=FSLoader(filesystem, *args, **kwargs),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

    @staticmethod
    def build_fs(filesystem, ctx):
        filesystem.makedir("dir")
        with ctx:
            nested = ctx << filesystem.open("dir/nested.j2", "w")
            nested.write("<html>this is a nested template !</html>")
        with ctx:
            top = ctx << filesystem.open("top.j2", "w")
            top.write("<html>this is a top level template !</html>")

    @staticmethod
    def build_zipfs():
        with fs.open_fs("zip://test.zip", create=True) as filesystem:
            filesystem.writetext("template_in_zip.j2", "<html>this template is in a zip</html>")

    @in_context
    def test_get_source_nosyspath_nourl(self, ctx):
        testfs = ctx << fs.open_fs('mem://')
        self.build_fs(testfs, ctx)

        env = self.build_env(testfs)
        template = env.get_template("dir/nested.j2")
        self.assertEqual(template.render(), "<html>this is a nested template !</html>")
        template = env.get_template("top.j2")
        self.assertEqual(template.render(), "<html>this is a top level template !</html>")
        self.assertRaises(jinja2.TemplateNotFound, env.get_template, "other.j2")
        source, path, _ = env.loader.get_source(None, "dir/nested.j2")
        self.assertEqual(path, "dir/nested.j2")

        env = self.build_env(testfs, use_syspath=True)
        source, path, _ = env.loader.get_source(None, "dir/nested.j2")
        self.assertEqual(path, "dir/nested.j2")

    @in_context
    def test_get_source_syspath(self, ctx):
        testfs = ctx << fs.open_fs("temp://")
        self.build_fs(testfs, ctx)

        env = self.build_env(testfs)
        template = env.get_template("dir/nested.j2")
        self.assertEqual(template.render(), "<html>this is a nested template !</html>")
        template = env.get_template("top.j2")
        self.assertEqual(template.render(), "<html>this is a top level template !</html>")
        self.assertRaises(jinja2.TemplateNotFound, env.get_template, "other.j2")
        source, path, _ = env.loader.get_source(None, "dir/nested.j2")
        self.assertEqual(path, "dir/nested.j2")

        env = self.build_env(testfs, use_syspath=True)
        source, path, _ = env.loader.get_source(None, "dir/nested.j2")
        self.assertEqual(path, os.path.join(testfs.getsyspath('/'), "dir", "nested.j2"))

    @in_context
    def test_get_source_nomtime(self, ctx):
        testfs = ctx << fs.open_fs("temp://")
        _getinfo = testfs.getinfo
        testfs.getinfo = lambda path, namespaces=None: _getinfo(path)
        self.build_fs(testfs, ctx)

        env = self.build_env(testfs)
        template = env.get_template("dir/nested.j2")
        self.assertEqual(template.render(), "<html>this is a nested template !</html>")
        template = env.get_template("top.j2")
        self.assertEqual(template.render(), "<html>this is a top level template !</html>")
        self.assertRaises(jinja2.TemplateNotFound, env.get_template, "other.j2")
        source, path, _ = env.loader.get_source(None, "dir/nested.j2")
        self.assertEqual(path, "dir/nested.j2")

        env = self.build_env(testfs, use_syspath=True)
        source, path, _ = env.loader.get_source(None, "dir/nested.j2")
        self.assertEqual(path, os.path.join(testfs.getsyspath('/'), "dir", "nested.j2"))

    @in_context
    def test_get_source_nosyspath_url(self, ctx):
        testfs = ctx << fs.open_fs("temp://")
        testfs.getinfo
        testfs.hassyspath = lambda path: False
        self.build_fs(testfs, ctx)

        env = self.build_env(testfs)
        template = env.get_template("dir/nested.j2")
        self.assertEqual(template.render(), "<html>this is a nested template !</html>")
        template = env.get_template("top.j2")
        self.assertEqual(template.render(), "<html>this is a top level template !</html>")
        self.assertRaises(jinja2.TemplateNotFound, env.get_template, "other.j2")
        source, path, _ = env.loader.get_source(None, "dir/nested.j2")
        self.assertEqual(path, "dir/nested.j2")

        env = self.build_env(testfs, use_syspath=True)
        source, path, _ = env.loader.get_source(None, "dir/nested.j2")
        self.assertEqual(path, "{}/dir/nested.j2".format(testfs.geturl('/').rstrip('/')))

    @in_context
    def test_list_templates(self, ctx):
        testfs = ctx << fs.open_fs("temp://")
        testfs.getinfo
        testfs.hassyspath = lambda path: False
        self.build_fs(testfs, ctx)

        env = self.build_env(testfs)
        self.assertEqual(env.loader.list_templates(), ["dir/nested.j2", "top.j2"])

    @in_context
    def test_multiple_fs(self, ctx):
        testfs = ctx << fs.open_fs('mem://')
        self.build_fs(testfs, ctx)
        self.build_zipfs()

        multi_fs = MultiFS()
        multi_fs.add_fs('memory', testfs)
        multi_fs.add_fs('zip', fs.open_fs("zip://test.zip"))

        env = self.build_env(multi_fs)
        template = env.get_template("dir/nested.j2")
        self.assertEqual(template.render(), "<html>this is a nested template !</html>")
        template = env.get_template("template_in_zip.j2")
        self.assertEqual(template.render(), "<html>this template is in a zip</html>")
        self.assertRaises(jinja2.TemplateNotFound, env.get_template, "other.j2")
        source, path, _ = env.loader.get_source(None, "template_in_zip.j2")
        self.assertEqual(path, "template_in_zip.j2")

    @in_context
    def test_multiple_fs_with_use_syspath(self, ctx):
        testfs = ctx << fs.open_fs('mem://')
        self.build_fs(testfs, ctx)
        self.build_zipfs()

        multi_fs = MultiFS()
        multi_fs.add_fs('memory', testfs)
        multi_fs.add_fs('zip', fs.open_fs("zip://test.zip"))

        env = self.build_env(multi_fs, use_syspath=True)
        source, path, _ = env.loader.get_source(None, "template_in_zip.j2")
        self.assertEqual(path, "template_in_zip.j2")
        os.unlink("test.zip")
