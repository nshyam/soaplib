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
    __namespace__ = "faz"

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
    __namespace__ = "baz"

    b = String()
    a = String()
    z = String()

class Bar(ClassModel):
    __namespace__ = "bar"
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

    baz = baz_factory()

    b.baz = baz

    return b

def baz_factory():
    baz = Baz()
    baz.b = "b"
    baz.a = "a"
    baz.z = "z"
    return baz

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

    def test_root_tag(self):
        mo = ModelOpener(Bar)
        xsd_doc = mo.get_schema_xml()
        schema = lxml.etree.fromstring(xsd_doc)
        root = schema.tag
        self.assertEquals(NS_SCHEMA, root)

    def test_bar_xsd_order(self):
        mo = ModelOpener(Bar)
        expected_children_order = ['b' , 'a', 'r', 'f', 'o', 'o_', 'b1', 'a2', 'r2', 'baz']
        for i in xrange(1000):
            bar_xsd = mo.get_schema_xml()
            bar_schema = lxml.etree.fromstring(bar_xsd)
            bar_xsd_children = bar_schema.xpath('/xs:schema/xs:complexType\
                                                 [@name="Bar"]/xs:sequence/xs:element', 
                                                 namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
            self.assertTrue(bar_xsd_children)
            self.assertEquals(expected_children_order, [child.get('name') for child in bar_xsd_children])

    def test_foo_xsd_order(self):
        expected_children_order = ['f' , 'o', 'o_', 'faz']
        foo = ModelOpener(Foo)
        for i in xrange(1000):
            foo_xsd = foo.get_schema_xml()
            foo_schema = lxml.etree.fromstring(foo_xsd)
            foo_xsd_children = foo_schema.xpath('/xs:schema/xs:complexType\
                                                 [@name="Foo"]/xs:sequence/xs:element', 
                                                 namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
            self.assertTrue(foo_xsd_children)
            self.assertEquals(expected_children_order, [child.get('name') for child in foo_xsd_children])

    def test_faz_xsd_order(self):
        expected_children_order = ['f' , 'a', 'z']
        faz = ModelOpener(Faz)
        for i in xrange(1000):
            faz_xsd = faz.get_schema_xml()
            faz_schema = lxml.etree.fromstring(faz_xsd)
            faz_xsd_children = faz_schema.xpath('/xs:schema/xs:complexType\
                                                 [@name="Faz"]/xs:sequence/xs:element', 
                                                 namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
            self.assertTrue(faz_xsd_children)
            self.assertEquals(expected_children_order, [child.get('name') for child in faz_xsd_children])

        #faz_element = self.schema[0]
        #expected_order = ["f","a", "z"]
        #order = [child.get('name') for child in faz_element.iter(NS_ELEMENT)]
        #self.assertEquals(expected_order, order)

    def test_baz_xsd_order(self):
        expected_children_order = ['b' , 'a', 'z']
        baz = ModelOpener(Baz)
        for i in xrange(1000):
            baz_xsd = baz.get_schema_xml()
            baz_schema = lxml.etree.fromstring(baz_xsd)
            baz_xsd_children = baz_schema.xpath('/xs:schema/xs:complexType\
                                                 [@name="Baz"]/xs:sequence/xs:element', 
                                                 namespaces={'xs':'http://www.w3.org/2001/XMLSchema'})
            self.assertTrue(baz_xsd_children)
            self.assertEquals(expected_children_order, [child.get('name') for child in baz_xsd_children])

class CustomizedInstanceTestCase(unittest.TestCase):

    def setUp(self):
        self.instance = bar_factory()
        self.mo = ModelOpener(Bar)
        self.xml = self.mo.get_instance_etree(self.instance)

    def test_children_tag_order(self):

        expected = [
            "{bar}b", "{bar}a", "{bar}r", "{bar}f", "{bar}o", "{bar}o_",
            "{bar}b1", "{bar}a2", "{bar}r2", "{bar}baz"
        ]
        
        self.assertEquals(
            expected,
            [n.tag for n in self.xml.iterchildren()]
        )
