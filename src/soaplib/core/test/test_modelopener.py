from StringIO import StringIO
from lxml import etree
import unittest
from soaplib.core.model.clazz import ClassModel
from soaplib.core.model.primitive import String, Integer
from soaplib.core.test.test_xml_output import (complex_factory, ComplexModel,
                                               simple_factory, SimpleModel,
                                               foo_metadata_factory, FooMetaDataXs,
                                               foo_child_factory_one, foo_child_factory_two,
                                               FooChildXs, foo_main_factory, 
                                               foo_main_factory_with_invalid_xml, FooMainXs)
from soaplib.core.util.model_utils import ModelOpener

class NoNillable(ClassModel):
    __namespace__ = "nn"
    a = String(nillable=False, min_occurs=1)
    i = Integer

class TestValidation(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_assert_incorrect_instance(self):
        opener = ModelOpener(ComplexModel)
        self.assertRaises(TypeError, opener.get_instance_etree, simple_factory())
        self.assertRaises(TypeError, opener.get_instance_xml, simple_factory())
        self.assertRaises(TypeError, opener.write_instance_xml, simple_factory())


    def test_get_instance_xml(self):
        opener = ModelOpener(ComplexModel)
        xml_string = opener.get_instance_xml(complex_factory())
        self.assertNotEquals(xml_string, None)
        self.assertNotEquals(xml_string,"")
        element = etree.fromstring(xml_string)

        chidren = [child for child in element]

        self.assertEqual(len(chidren), 4)
        tag_contains = "complexmodel" in element.tag
        #TODO: Clean up this test, it seems a bit magical
        #TODO: Search the sub tags.
        #TODO: Search the sub values
        self.assertTrue(tag_contains)

    def test_get_instance_etree(self):
        opener = ModelOpener(ComplexModel)
        element = opener.get_instance_etree(complex_factory())
        chidren = [child for child in element]

        self.assertEqual(len(chidren), 4)
        tag_contains = "complexmodel" in element.tag
        #TODO: Clean up this test, it seems a bit magical
        #TODO: Search the sub tags.
        #TODO: Search the sub values
        self.assertTrue(tag_contains)


    def test_valid(self):
        complex = complex_factory()
        opener = ModelOpener(ComplexModel)
        valid, log = opener.validate_instance(complex)
        
        self.assertTrue(valid)
        self.assertEquals(len(log), 0)

    def test_invalid(self):
        # Created two validation errors here
        # 1) a is not nillable
        # 2) i must be type xs:integer
        n = NoNillable()
        n.i = "A"

        opener = ModelOpener(NoNillable)
        valid, log = opener.validate_instance(n)
        self.assertFalse(valid)
        self.assertEquals(len(log), 2)



        opener = ModelOpener(ComplexModel)
        xml_string = opener.get_instance_xml(complex_factory())
        self.assertNotEquals(xml_string, None)
        self.assertNotEquals(xml_string,"")
        element = etree.fromstring(xml_string)


    def test_validate_valid_complex_xml_against_xsd(self):
        ns_map = {"foo":"foo"}
        foo_main = foo_main_factory()
        opener = ModelOpener(FooMainXs, custom_ns_map=ns_map)
        xml_string = opener.get_instance_xml(foo_main_factory())
        print xml_string

        valid, log = opener.validate_instance(foo_main)
        assert valid == True


    def test_validate_invalid_complex_xml_against_xsd(self):
        ns_map = {"foo":"foo"}
        foo_main = foo_main_factory_with_invalid_xml()
        opener = ModelOpener(FooMainXs, custom_ns_map=ns_map)
        xml_string = opener.get_instance_xml(foo_main_factory_with_invalid_xml())
        print xml_string

        valid, log = opener.validate_instance(foo_main)
        # i am assuming here it should fail here ..but its not failing
        assert valid == False


        


