
#!/usr/bin/env python
#
# soaplib - Copyright (C) Soaplib contributors.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#

import unittest
import os
from datetime import datetime
from lxml import etree

from soaplib.core.model.clazz import ClassModel
from soaplib.core.model.primitive import Integer, String, DateTime
from soaplib.core.util.model_utils import ClassModelConverter

class SimpleModel(ClassModel):

    __namespace__ = "simplemodel"
    __type_name__ = "simplemodel"
    simple_text = String
    simple_num = Integer
    simple_date = DateTime

def simple_factory():
    simple = SimpleModel()
    simple.simple_text = "Text"
    simple.simple_num = 1234
    simple.simple_date = datetime(2001, 12, 12)
    return simple


class ComplexModel(ClassModel):
    __namespace__ = "complexmodel"
    __type_name__ = "complexmodel"
    simple = SimpleModel
    complex_text = String
    complex_num = Integer
    complex_date = DateTime


def complex_factory():
    simple = simple_factory()
    complex = ComplexModel()
    complex.simple = simple
    complex.complex_text = "ComplexText"
    complex.complex_num = 2222
    complex.complex_date = datetime(2010, 1, 1)
    return complex




class BaseCase(unittest.TestCase):

    def setUp(self):
        self.file_path = "instance.xml"
        self.converter = ClassModelConverter(complex_factory(), "complexmodel")

    def tearDown(self):
        if os.path.isfile(self.file_path):
            os.unlink(self.file_path)

    def xml(self):
        xml = self.converter.to_xml()
        self.assertTrue(xml)

    def file(self):
        self.converter.to_file(self.file_path)
        self.assertTrue(os.path.isfile(self.file_path))

    def element(self):
        element =  self.converter.to_etree()
        self.assertTrue(element)

        print etree.tostring(element, pretty_print=True)

        tns_tag = '{%s}%s' % \
                  (self.converter.instance.get_namespace(), self.converter.instance.__type_name__)
        self.assertEquals(element.tag, tns_tag)

    def remove_ns(self):
        self.converter.include_ns = False
        element = self.converter.to_etree()
        self.assertFalse(element.nsmap)



class ModelAsRootTestCase(BaseCase):

    def test_simple_xml(self):
        self.xml()

    def test_simple_file(self):
        self.file()

    def test_complex_xml(self):
        self.xml()

    def test_complex_file(self):
        self.file()

    def test_strip_ns(self):
        self.remove_ns()


class AddedRootElementTestCase(BaseCase):
    def setUp(self):
        self.file_path = "instance.xml"
        self.converter = ClassModelConverter(
                simple_factory(),"tns", parent_tag="foo")

    def element(self):
        element =  self.converter.to_etree()
        self.assertTrue(element)
        self.assertEquals(element.tag, self.converter.parent_tag)

    def test_simple_xml(self):
        self.xml()

    def test_simple_file(self):
        self.file()

    def test_simple_element(self):
        self.element()

    def test_complex_xml(self):
        self.xml()

    def test_complex_file(self):
        self.file()

    def test_complex_element(self):
        self.element()

    def test_strip_ns(self):
        self.remove_ns()

class NillMinOccursModel(ClassModel):
    __namespace__ = "tns"

    nillable_only = String(nillable=True, min_occurs=1)
    nillabl_min_occ_zero = String(nillable=True, min_occurs=0)
    min_occ_int = Integer(nillable=True, min_occurs=1)