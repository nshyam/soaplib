import unittest
from soaplib.core.model.clazz import ClassModel
from soaplib.core.model.primitive import String, Integer, Date
from soaplib.core.util.model_utils import ModelOpener

class ManySimpleElements(ClassModel):
    s1 = String()
    i1 = Integer()
    s2 = String()
    i2 = Integer()
    s3 = String()
    i3 = Integer()
    s4 = String()
    i4 = Integer()
    s5 = String()
    i5 = Integer()
    s6 = String()
    i6 = Integer()
    s7 = String()
    i7 = Integer()
    s8 = String()
    i8 = Integer()
    s9 = String()
    i9 = Integer()
    s10 = String()
    i10 = Integer()

class ComplexModel(ClassModel):
    mse = ManySimpleElements
    mse2 = ManySimpleElements

def many_simple_factory():
    mse = ManySimpleElements()
    mse.s1 = "s1"
    mse.i1 = 1
    mse.s2 = "s2"
    mse.i2 = 2
    mse.s3 = "s3"
    mse.i3 = 3
    mse.s4 = "s4"
    mse.i4 = 4
    mse.s5 = "s5"
    mse.i5 = 5
    mse.s6 = "s6"
    mse.i6 = 6
    mse.s7 = "s7"
    mse.i7 = 7
    mse.s8 = "s8"
    mse.i8 = 8
    mse.s9 = "s9"
    mse.i9 = 9
    mse.s10 = "s10"
    mse.i10= 10

    return mse

def complex_factory():
    c = ComplexModel()
    mse = many_simple_factory()
    mse1 = many_simple_factory()
    c.mse = mse
    c.ms2 = mse1

class TestSquenceOrder(unittest.TestCase):

    def setUp(self):
        self.simple = many_simple_factory()
        self.foo = 'bar'

    def tearDown(self):
        pass

    def test_sequence_always_the_same(self):
        mo = ModelOpener(ManySimpleElements)
        # Testing that the output for the schema is *always the same*
        out = mo.get_schema_xml()
        print out
        el = mo.get_schema_etree()

        inst = mo.get_instance_xml(many_simple_factory())
        print inst

        for x in xrange(1000):
            self.assertEquals(el, mo.get_schema_etree())