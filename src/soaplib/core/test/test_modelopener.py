from StringIO import StringIO
from lxml import etree
import unittest
from soaplib.core.model.clazz import ClassModel
from soaplib.core.model.primitive import String, Integer
from soaplib.core.test.test_xml_output import complex_factory, ComplexModel, simple_factory, SimpleModel
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
