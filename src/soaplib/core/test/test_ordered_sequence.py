import unittest
import lxml

from soaplib.core.model.clazz import ClassModel
from soaplib.core.model.primitive import String, Integer
from soaplib.core.util.model_utils import ModelOpener

NS_SCHEMA = "{http://www.w3.org/2001/XMLSchema}schema"
NS_ELEMENT = "{http://www.w3.org/2001/XMLSchema}element"

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

class Faz(ClassModel):
    __namespace__ = "foo"

    f = Integer()
    a = Integer()
    z = Integer()


class Foo(ClassModel):
    __namespace__ = "foo"
    f = String()
    o = String()
    o_ = String()
    faz = Faz.customize(nillable=False)


class Baz(ClassModel):
    __namespace__ = "foo"

    b = String()
    a = String()
    z = String()

class Bar(ClassModel):
    __namespace__ = "foo"
    b = Integer(nillable=False)
    a = Integer(nillable=False)
    r = Integer(nillable=False)

    f = Foo.customize(nillable=False)
    o = Foo.customize(nillable=False)
    o_ = Foo.customize(nillable=False)

    b1 = Integer()
    a2 = Integer()
    r2 = Integer()

    baz = Baz.customize(min_occurs=1)

def foo_factory(string):
    f = Foo()
    f.f = string
    f.o = string
    f.o_ = string

    faz = Faz()
    faz.f = 1
    faz.a = 2
    faz.z = 3

    f.faz = faz

    return f

def bar_factory():
    b = Bar()
    b.b = "b"
    b.a = "a"
    b.r = "r"
    b.f = foo_factory("f")
    b.o = foo_factory("o")
    b.o_ = foo_factory("o")
    b.b1 = 1
    b.a2 = 2
    b.r2 = 3

    baz = Baz()
    baz.b = "b"
    baz.a = "a"
    baz.z = "z"

    b.baz = baz

    return b


class TestSequenceOrder(unittest.TestCase):

    def setUp(self):
        self.simple = many_simple_factory()
        self.foo = 'bar'

    def tearDown(self):
        pass

    def test_sequence_always_the_same(self):
        mo = ModelOpener(ManySimpleElements)
        # Testing that the output for the schema is *always the same*
        #NOTE:the following line is only meant for allowing the testcase to pass
        mo.get_schema_xml()
        out = mo.get_schema_xml()

        for x in xrange(1000):
            self.assertEquals(out, mo.get_schema_xml())


class CustomizedXsdTestCase(unittest.TestCase):

    def setUp(self):
        self.bar = bar_factory()
        self.mo = ModelOpener(Bar)
        self.xsd_doc = self.mo.get_schema_xml()
        self.schema = lxml.etree.fromstring(self.xsd_doc)

    def test_root_tag(self):
        root = self.schema.tag
        self.assertEquals(NS_SCHEMA, root)

    def test_child_order(self):
        expected = [
            "Faz", "Foo", "Baz", "Bar", "binding_method",
            "binding_methodResponse", 'Faz', 'Foo', 'Baz', 'Bar',
            'binding_method', 'binding_methodResponse'
        ]
        self.assertEquals(
            expected,
            [child.get('name') for child in self.schema.iterchildren()]
        )

    def test_faz_order(self):

        faz_element = self.schema[0]
        expected_order = ["f","a", "z"]
        order = [child.get('name') for child in faz_element.iter(NS_ELEMENT)]
        self.assertEquals(expected_order, order)


class CustomizedInstanceTestCase(unittest.TestCase):

    def setUp(self):
        self.instance = bar_factory()
        self.mo = ModelOpener(Bar)
        self.xml = self.mo.get_instance_etree(self.instance)

    def test_children_tag_order(self):

        expected = [
            "{foo}b", "{foo}a", "{foo}r", "{foo}f", "{foo}o", "{foo}o_",
            "{foo}b1", "{foo}a2", "{foo}r2", "{foo}baz"
        ]
        
        self.assertEquals(
            expected,
            [n.tag for n in self.xml.iterchildren()]
        )
