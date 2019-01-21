# coding: utf-8
from __future__ import unicode_literals

import unittest
import os

import contexter
import fs
import jinja2

from jinja2_fsloader import FSLoader
from .utils import in_context, mock





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
        _getinfo = testfs.getinfo
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
        _getinfo = testfs.getinfo
        testfs.hassyspath = lambda path: False
        self.build_fs(testfs, ctx)

        env = self.build_env(testfs)
        self.assertEqual(env.loader.list_templates(), ["dir/nested.j2", "top.j2"])

