"""Utility classes and methods for converting and validating
soaplib.core.model.ClassModel instances
"""
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

    def __init__(self, model_instance, include_parent=False, parent_tag="root", include_ns=True):
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
        self.prefix_by_namespace = defaultdict(list)

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
        gen = XSDGenerator()
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


        for ns,prefix in self.prefix_by_namespace.items():
            if ns not in root_ns_map.values():
                root_ns_map[prefix[0]] = ns

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

        clean_root = self._simplify_imports(rt_el)
        root_ns_prefix = self.prefix_by_namespace[self.instance.get_namespace()][0]
        schema_location = "%s file:%s" % (root_ns_prefix ,self._get_xsd_import_name())
        clean_root.set("{%s}%s" % (namespaces.ns_xsi, "schemaLocation"), schema_location)

        return clean_root


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

        @param The output file path for the xml file
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