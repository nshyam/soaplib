"""Utility classes and methods for converting and validating
soaplib.core.model.ClassModel instances
"""
from StringIO import StringIO
from _collections import defaultdict
import shutil
import tempfile

import os
import re
from lxml import etree
from soaplib.core import namespaces

from soaplib.core.util.xsd_gen import XSDGenerator

class ClassModelConverter():
    """A class to handle exporting a ClassModel to different representations

    Currently supported export targets are lxml.etree.Element, string and
    xml documents.

    This functionality will most likely be moved into the ClassModel itself if
    it proves useful and there is a willingness to modify the current
    ClassModel API.
    """

    xml_instance_ns_map = {
        'xs': namespaces.ns_xsd,
        'xsi': namespaces.ns_xsi,
        }

    def __init__(self, model_instance, include_parent=False, parent_tag="root", include_ns=True, custom_nsmap=None):
        """
        @param model_instance: An instance of a soaplib.core.model.clazz.ClassModel
        @param include_parent: Indicates if a parent element should be returned as the root
        element of the xml representation.  If true, a root element will be included with
        the tag "parent_tag"
        @param parent_tag: The tag used for the creation of a root/parent element.
        """

        self.instance = model_instance
        self.include_parent= include_parent
        self.parent_tag = parent_tag
        self.include_ns = include_ns
        self.custom_nsmap = custom_nsmap
        self.prefix_by_namespace = defaultdict(list)

        if custom_nsmap:
            for prefix, namespace in self.custom_nsmap.items():
                self.prefix_by_namespace[namespace].append(prefix)


    def __get_ns_free_element(self, element):
        """ """

        new_el = None
        m = re.search('(?<=})\w+', element.tag)

        if m:
            new_el = etree.Element(m.group(0))
        else:
            new_el = etree.Element(element.tag)

        new_el.text = element.text

        for k in element.attrib.keys():
            if k not in ["{http://www.w3.org/2001/XMLSchema-instance}nil"]:
                new_el.attrib[k] = element.attrib[k]

        for child in element.iterchildren():
            new_child = self.__get_ns_free_element(child)
            new_el.append(new_child)

        return new_el



    def _get_xsd_import_name(self):
        """Returns the name of the documents xsd for building the correct
        schemaLocation statement
        """
        gen = XSDGenerator(custom_ns_map=self.custom_nsmap)
        tmp_dir_name = tempfile.mkdtemp()
        file_name = gen.write_model_xsd_file(self.instance.__class__, tmp_dir_name)
        shutil.rmtree(tmp_dir_name)


        return os.path.basename(file_name)



    def _rebuild_root(self, old_root, new_root):

        for child in old_root.iterchildren():
            new_sub = etree.SubElement(new_root, child.tag, attrib=child.attrib)
            new_sub.text = child.text
            self._rebuild_root(child, new_sub)


    def _simplify_imports(self, root):

        root_ns_map = root.nsmap
        for prefix, ns in ClassModelConverter.xml_instance_ns_map.items():
            root_ns_map[prefix] = ns

        self._build_defult_prefix_by_namespace(root)

        for namespace,prefix in self.prefix_by_namespace.items():
            for root_prf,root_ns in root_ns_map.items():
                if root_ns == namespace:
                    del root_ns_map[root_prf]

                root_ns_map[prefix[0]] = namespace


        new_root = etree.Element(root.tag, nsmap=root_ns_map, attrib=root.attrib)
        self._rebuild_root(root, new_root)

        return new_root


    def _build_defult_prefix_by_namespace(self, root):
        dirty_children = [child for child in root.iterchildren()]

        if dirty_children:
            for child in dirty_children:
                for prefix,namespace in child.nsmap.items():
                    if prefix not in self.prefix_by_namespace[namespace]:
                        self.prefix_by_namespace[namespace].append(prefix)

            for child in dirty_children:
                self._build_defult_prefix_by_namespace(child)



    def __get_etree(self):
        root_element = etree.Element(self.parent_tag)
        self.instance.to_parent_element(self.instance, self.instance.get_namespace(), root_element)

        if not self.include_parent:
            rt_el = root_element[0]
        else:
           rt_el = root_element

        if not self.include_ns:
            rt_el = self.__get_ns_free_element(rt_el)

        if self.include_ns:
            clean_root = self._simplify_imports(rt_el)

            #TODO: Handle the case when a model does not have a ns!!!

            root_ns_prefix = self.prefix_by_namespace[self.instance.get_namespace()][0]
            schema_location = "%s file:%s" % (root_ns_prefix ,self._get_xsd_import_name())
            clean_root.set("{%s}%s" % (namespaces.ns_xsi, "schemaLocation"), schema_location)
            return clean_root
        else:
            return rt_el


    def to_etree(self):
        """Returns a lxml.etree.Element from a soaplib.core.model.clazz.ClassModel
        instance.
        """

        return self.__get_etree()



    def to_xml(self):
        """Returns a xml string from a soaplib.core.model.clazz.ClassModel instance.
        """
        el = self.to_etree()

        return etree.tostring(
                    el,
                    pretty_print=True,
                    encoding="UTF-8",
                    xml_declaration=True
                    )


    def to_file(self, file_path):
        """Writes a model instance to a XML document

        @param: file_path The output file path for the xml file
        """

        el = self.to_etree()

        f = open(file_path, "w")

        etree.ElementTree(el).write(
            f,
            pretty_print=True,
            encoding="UTF-8",
            xml_declaration=True
            )

        f.close()


class ModelOpener(object):
    """Simple Interface for simple XML and XSD generation"""

    def __init__(self, model, custom_ns_map=None):
        self.model = model
        self.custom_ns_map = custom_ns_map
        self.xsd_gen = XSDGenerator(self.custom_ns_map)
        self.xsd_list = None

    def validate_instance(self, instance):
        # 1) Generate the schemas, due to the possibility that there may be more than one xsd involved will need to write these to a temp file
        # -> check to see if the files have already been written, if not write them to a temp location

        xsd_dir = None
        temp_used = False
        if not self.xsd_list:
            temp_used = True
            xsd_dir = tempfile.mkdtemp()
            self.write_schemas(xsd_dir)
        else:
            xsd_dir = os.path.dirname(self.xsd_list[0])

        xsd_full_path = self.xsd_gen.write_model_xsd_file(self.model, xsd_dir)

        with open(xsd_full_path) as file_handler:
            schema_doc = etree.parse(file_handler)

        model_xsd = etree.XMLSchema(schema_doc)

#        xsd_name = self.xsd_gen.__get_xsd_file_name(self.model, None)
#        xsd_full_path = os.path.join(xsd_dir, xsd_name)

        # 2) Build a lxml XML Schema.
#        model_xsd = self.get_schema_etree()


        # 3) Write the instance XML to a stream and then parse that into an lxml etree
        doc = etree.parse(StringIO(self.get_instance_xml(instance)))
        # 4) Run lxml assertValid. If it is invalid the capture the log

        valid = model_xsd.validate(doc)
        if temp_used:
            shutil.rmtree(xsd_dir)

        # 5) Return a tuple containing the validation state and the log.
        return valid, model_xsd.error_log
    

    def __instance_of_model(self, instance):
        """Validates that the instance is indeed and instance of the Model
        class passed in the init method
        """
        if not isinstance(instance, self.model):
            msg = """Expected instance of {0:>s} but the instance belongs to
            the class {1:>s}""".format(
                self.model.__name__,
                instance.__class__.__name__)

            raise TypeError(msg)


    def __get_instance_converter(self, instance):
        """Generates an instance of util.model_utils.ClassModelConverter for
        the given instance.
        """

        self.__instance_of_model(instance)
        return ClassModelConverter(instance, custom_nsmap=self.custom_ns_map)

    def get_instance_xml(self, instance):
        """Returns a xml string for the given model instance
        """

        return self.__get_instance_converter(instance).to_xml()

    def get_instance_etree(self, instance):
        """Returns a lxml.etre._Element instance for the given model instance.
        """

        return self.__get_instance_converter(instance).to_etree()

    def write_instance_xml(self, instance, destination_file):
        """ Writes an xml file to the given destination for the given model
        instance
        """

        return self.__get_instance_converter(
            instance).to_file(destination_file
            )

    def get_schema_xml(self):
        """Returns a string representation of an XSD for the specified model.
        """
        return self.xsd_gen.get_model_xsd(self.model)

    def get_schema_etree(self):
        xsd_string = StringIO(self.get_schema_xml())
        xsd_doc = etree.parse(xsd_string)

        return etree.XMLSchema(xsd_doc)

    def write_schemas(self, folder_path):
        """Writes the XML Schema for the model.
        
        This method also generates all schemas that the model may be importing.

        @param folder_path:  The destination path for the XML Schemas
        """
        self.xsd_list = self.xsd_gen.write_all_models(self.model, folder_path)
        return self.xsd_list