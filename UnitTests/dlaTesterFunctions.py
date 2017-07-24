import functools
import os
import pathlib
import xml.etree.ElementTree as ET
import zipfile

import arcpy
import pandas as pd

import dla
from inc_datasources import _XMLMethodNames, _localWorkspace, _outputDirectory
from test_All import UnitTests

pd.set_option('display.width', 1000)


# the dla.gdb is the test workspace the feature classes are created in. To pull the one we want, we clear the workspace
# so that the newly created one is the only one that exists. This function clears the workspace.
def clearFeatureClasses(directory):
    arcpy.env.workspace = directory
    featureclasses = arcpy.ListFeatureClasses()
    for featureclass in featureclasses:
        arcpy.Delete_management(os.path.join(directory, featureclass))


# takes the xml file and creates the fields that should be in the new feature class
def build_correct_fields(xmlLocation):
    fields = dla.getXmlElements(xmlLocation, "Field")
    correct_fields = []
    for field in fields:
        if str.lower(dla.getNodeValue(field, "TargetName")) != "globalid":
            correct_fields.append(dla.getNodeValue(field, "TargetName"))
    return correct_fields


def make_copy(directory):
    clearFeatureClasses(directory)  # creating a copy of the target feature class
    arcpy.env.workspace = _localWorkspace["Target"]  # to compare to after append
    arcpy.CopyFeatures_management("Target", os.path.join(directory, "copy"))


def restore_data():
    """
    After the data is replaced or appended, this function will restore the target to the original state
    :param path_to_zip:
    :return:
    """
    workspace = str(pathlib.Path(".\localData").absolute())
    for file in os.listdir(workspace):
        if ".zip" in file:
            with zipfile.ZipFile(file) as unzipper:
                unzipper.extractall(workspace)  # TODO: change workspace here to the address to a temp folder


# taken from https://bitbucket.org/ianb/formencode/src/tip/formencode/doctest_xml_compare.py?fileviewer=file-view-default#cl-70
def xml_compare(x1, x2, reporter=None):
    if x1.tag != x2.tag:
        if reporter:
            reporter('Tags do not match: %s and %s' % (x1.tag, x2.tag))
        return False
    for name, value in x1.attrib.items():
        if x2.attrib.get(name) != value:
            if reporter:
                reporter('Attributes do not match: %s=%r, %s=%r'
                         % (name, value, name, x2.attrib.get(name)))
            return False
    for name in x2.attrib.keys():
        if name not in x1.attrib:
            if reporter:
                reporter('x2 has an attribute x1 is missing: %s'
                         % name)
            return False
    if not text_compare(x1.text, x2.text):
        if reporter:
            reporter('text: %r != %r' % (x1.text, x2.text))
        return False
    if not text_compare(x1.tail, x2.tail):
        if reporter:
            reporter('tail: %r != %r' % (x1.tail, x2.tail))
        return False
    cl1 = x1.getchildren()
    cl2 = x2.getchildren()
    if len(cl1) != len(cl2):
        if reporter:
            reporter('children length differs, %i != %i'
                     % (len(cl1), len(cl2)))
        return False
    i = 0
    for c1, c2 in zip(cl1, cl2):
        i += 1
        if not xml_compare(c1, c2, reporter=reporter):
            if reporter:
                reporter('children %i do not match: %s'
                         % (i, c1.tag))
            return False
    return True


def text_compare(t1, t2):
    if not t1 and not t2:
        return True
    if t1 == '*' or t2 == '*':
        return True
    return (t1 or '').strip() == (t2 or '').strip()


class Helper(object):
    """
    Class designed to run all of the tests for any test object, whether it be Preview, Stage, Append, or Replace
    """

    def __init__(self, tester: UnitTests, test_object, lw, tc):
        self.tester = tester
        self.testObject = test_object
        self.local_workspace = lw
        self.TestCase = tc
        self.localDirectory = _outputDirectory
        self.sourceWorkspace = lw["Source"]
        self.targetWorkspace = lw["Target"]
        self.sourceFC = lw["SourceName"]
        self.targetFC = lw["TargetName"]
        self.localFC = arcpy.ListFeatureClasses(self.localDirectory)[0]
        self.sourceDataPath = os.path.join(lw["Source"], lw["SourceName"])
        self.targetDataPath = os.path.join(lw["Target"], lw["TargetName"])
        self.localDataPath = os.path.join(_outputDirectory, self.localFC)
        self.sourceFields = tuple(arcpy.ListFields(self.sourceDataPath))
        self.targetFields = tuple(arcpy.ListFields(self.targetDataPath))
        self.localFields = tuple(arcpy.ListFields(self.localDataPath))
        self.methods = _XMLMethodNames
        self.xmlLocation = self.TestCase["xmlLocation"]
        self.outXML = tc["outXML"]
        self.correctXML = tc["correctXML"]

    @staticmethod
    @functools.lru_cache()
    def build_data_frame(directory, columns):
        """
        Builds and caches a pandas DataFrame object containing the information from the specified feature class
        :param directory: str
        :param columns: tupe(str)
        :return: pd.DataFrame object
        """
        # creates a searchCursor for a given feature class and returns an array of that table
        return pd.DataFrame(list(arcpy.da.SearchCursor(directory, columns)), columns=columns)

    @functools.lru_cache()
    def get_xml_parse(self):
        """
        Returns and caches a SourceTargetParser object containing information in it from the specified
        SourceTarget.xml file
        :return: SourceTargetParser object
        """
        return SourceTargetParser(self.xmlLocation)

    def test_fields(self):
        """
        Compares the xml file with the mutated file to ensure that the fields were correctly transferred over
        and not tampered with
        :return:
        """
        # TODO: Currently omitting GlobalID checks
        correct_fields = build_correct_fields(self.xmlLocation)
        if self.testObject.title in ["Append", "Replace"]:
            fields = arcpy.ListFields(self.targetDataPath)
        else:
            fields = arcpy.ListFields(self.localDataPath)

        fieldnames = []
        for field in fields:
            if field.name.lower() not in ["", "objectid", "shape", "globalid"]:
                fieldnames.append(field.name)

        for cfield in correct_fields:
            self.tester.assertIn(fieldnames, cfield)

    def test_length(self):
        """
        Ensures that the mutated file, depending on which it is, is the correct needed length
        :return:
        """
        source_table = self.build_data_frame(self.sourceDataPath, self.sourceFields)
        local_table = self.build_data_frame(self.localDataPath, self.sourceFields)
        target_table = self.build_data_frame(self.targetDataPath, self.targetFields)
        mode = self.testObject.title  # variable assignment to help with readability
        if mode == "Preview":
            if len(source_table) < self.testObject.RowLimit:
                self.tester.assertEqual(len(local_table), len(source_table))
            else:
                self.tester.assertEqual(len(local_table), self.testObject.Rowlimit)
        elif mode == "Stage":
            self.tester.assertEqual(len(local_table), len(source_table))
        elif mode == "Append":
            self.tester.assertEqual(len(target_table), len(local_table) + len(source_table))
        elif mode == "Replace":
            self.tester.assertEqual(len(target_table), len(local_table))
        else:
            self.tester.assertIn(mode, ["Preview", "Stage", "Append", "Replace"])

    def test_replace_data(self):
        """
        Ensures the correct rows were appended and removed and in the correct order
        :return:
        """
        replaced_rows_list = []
        copy = self.build_data_frame(self.localDataPath, self.localFields).iterrows()
        target = self.build_data_frame(self.targetDataPath, self.targetFields).iterrows()
        replace_dict = self.get_xml_parse().parse_replace()
        for copy_row, targetRow in zip(copy, target):  # will iterate through until all of the copy cursor is exhausted
            while targetRow != copy_row:
                if replace_dict["Operator"] == "=":
                    self.tester.assertEqual(targetRow[replace_dict["FieldName"]], replace_dict["Value"])
                if replace_dict["Operator"] == "!=":
                    self.tester.assertNotEqual(targetRow[replace_dict["FieldName"]], replace_dict["Value"])
                if replace_dict["Operator"] == "Like":
                    self.tester.assertIn(replace_dict["Value"], targetRow[replace_dict["FieldName"]])
                replaced_rows_list.append(copy_row)
                copy_row = copy.next()

        for targetRow, copy_row in zip(target,
                                       replaced_rows_list):  # now iterates through the rows that should have been
            self.tester.assertEqual(targetRow,
                                    copy_row)  # appended to ensure order and accuracy. Here the target cursor starts
            # at where the beginning of the re-appended rows should be

    def test_data(self):
        """
        Ensures that the mutated file has the correct data in each row, and that the data asisstant actions were
        performed correctly
        :return:
        """
        source_table = self.build_data_frame(self.sourceDataPath, self.sourceFields)
        local_table = self.build_data_frame(self.localDataPath, self.localFields)
        target_table = self.build_data_frame(self.targetDataPath, self.targetFields)
        xml_fields = self.get_xml_parse().get_pairings()
        method_dict = self.get_xml_parse().get_methods()
        xml_data = self.get_xml_parse.Data

        if self.testObject.title in ["Preiview", "Stage"]:  # needed so that we can use the same function to test append
            target = local_table
        else:
            self.tester.assertEqual(target_table.iloc[:len(local_table)], local_table)
            target = target_table.iloc[len(local_table):]  # ensures we are only comparing the newly appended data

        for field in xml_fields.keys():
            if method_dict[field] == self.methods["None"]:
                self.test_none(target[field])
            elif method_dict[field] == self.methods["Copy"]:
                self.test_copy(source_table[xml_fields[field]], target[field])
            elif method_dict[field] == self.methods["Set Value"]:
                self.test_set_value(target[field], xml_data[field][self.methods["Set Value"]])
            elif method_dict[field] == self.methods["Value Map"]:
                self.test_value_map(source_table[xml_fields[field]], target[field],
                                    xml_data[field][self.methods["Value Map"]], xml_data[field]["Otherwise"])
            elif method_dict[field] == self.methods["Change Case"]:
                self.test_change_case(source_table[xml_fields[field]], target[field],
                                      xml_data[field][self.methods["Change Case"]])
            elif method_dict[field] == self.methods["Concatenate"]:
                self.test_concatenate(target[field], xml_data[field]["Separator"],
                                      xml_data[field]["Concatenate"])
            elif method_dict[field] == self.methods["Left"]:
                self.test_left(source_table[xml_fields[field]], target[field], xml_data[field]["Left"])
            elif method_dict[field] == self.methods["Right"]:
                self.test_right(source_table[xml_fields[field]], target[field], xml_data[field]["Right"])
            elif method_dict[field] == self.methods["Substring"]:
                self.test_substring(source_table[xml_fields[field]], target[field], xml_data[field]["Start"],
                                    xml_data[field]["Length"])
            elif method_dict[field] == self.methods["Split"]:
                self.test_split(source_table[xml_fields[field]], target[field], xml_data[field]["SplitAt"],
                                xml_data[field]["Part"])
            elif method_dict[field] == self.methods["Conditional Value"]:
                self.test_conditional_value(source_table[xml_fields[field]], target[field],
                                            xml_data[field]["Oper"], xml_data[field]["If"], xml_data[field]["Then"],
                                            xml_data[field]["Else"])
            elif method_dict[field] == self.methods["Domain Map"]:
                self.test_domain_map(source_table[xml_fields[field]], target[field], xml_data[field]["Domain Map"])
            else:
                self.tester.assertIn(method_dict[field], self.methods)

    def test_none(self, target):
        """
        Ensures that the vector is a vector of none
        :param target:
        :return:
        """
        self.tester.assertTrue(len(target.unique()) == 1 and target.unique()[0] is None)

    def test_copy(self, source, target):
        """
         Ensures that the copy source got copied to the target. In other words, ensures that the two vectors are equal.
        """
        self.tester.assertTrue(source.equals(target))

    def test_set_value(self, target, value):
        """
        Ensures that the target values are all set properly
        :param target:
        :param value:
        :return:
        """
        self.tester.assertTrue(len(target.unique()) == 1 and target.unique() == value)

    def test_value_map(self, source, target, value_dict, otherwise):
        """
        Ensures the values are set to what they need to be based on the preset configuration in the value map
        :param source:
        :param target:
        :param value_dict
        :param otherwise
        :return:
        """
        for s, t in zip(source, target):
            if s in value_dict:
                self.tester.assertTrue(t == value_dict[s])
            else:
                self.tester.assertTrue(t == otherwise)

    def test_change_case(self, source, target, manipulation):
        """
        Ensures the row correctly was changed
        :param source:
        :param target:
        :param manipulation: str
        :return:
        """
        if manipulation == "UpperCase":
            self.tester.assertEqual(source, target.str.upper())
        elif manipulation == "Lowercase":
            self.tester.assertEqual(source, target.str.lower())
        elif manipulation == "Capitalize":
            self.tester.assertEqual(source, target.str.capitalize())
        elif manipulation == "Title":
            self.tester.assertEqual(source, target.str.title())
        else:
            self.tester.assertIn(manipulation, ["UpperCase", "Lowercase", "Capitalize", "Title"])

    def test_concatenate(self, target: pd.DataFrame, seperator: str,
                         cfields: list):  # TODO: Ensure test is working correctly
        """
        Ensures the row concatenates the correct field values
        :param target:
        :param seperator:
        :param cfields:
        :return:
        """
        source_table = self.build_data_frame(self.sourceDataPath, self.sourceFields)
        if seperator == "(space)":
            seperator = " "
        compare_column = source_table[cfields.pop()]
        for cifeld in cfields:
            compare_column = compare_column.astype(str).str.cat(source_table[cifeld].astype(str), sep=seperator)
        self.tester.assertEqual(target.astype(str), compare_column)

    def test_left(self, source: pd.DataFrame, target: pd.DataFrame, number: int):
        """
        Ensures the correct number of charcters from the left were mapped
        :param source:
        :param target
        :param number: int
        :return:
        """
        self.tester.assertEqual(source.str[number:], target)

    def test_right(self, source: pd.DataFrame, target: pd.DataFrame, number: int):
        """
        Ensures the correct number of characters from the right were mapped
        :param source:
        :param target:
        :param number:
        :return:
        """
        self.tester.assertEqual(source.str[-number:], target)

    def test_substring(self, source: pd.DataFrame, target: pd.DataFrame, start: int, length: int):
        """
        Ensures the correct substring was pulled from each row
        :param source:
        :param target:
        :param start:
        :param length:
        :return:
        """
        self.tester.assertEqual(source.str[start:length + start], target)

    def test_split(self, source: pd.DataFrame, target: pd.DataFrame, split_point: str, part: int):
        """
        Ensures the correct split was made and the resulting data is correct
        :param source:
        :param target:
        :param split_point:
        :param part:
        :return:
        """
        for sfield, tfield in zip(source, target):
            self.tester.assertEqual(sfield.split(split_point)[part], tfield)

    def test_conditional_value(self, source: pd.DataFrame, target: pd.DataFrame, oper: str, if_value,
                               then_value, else_value):
        """
        Ensures that the conditional value evaluates correctly in each row of the column
        :param source:
        :param target:
        :param oper:
        :param if_value:
        :param then_value:
        :param else_value:
        :return:
        """
        for sfield, tfield in zip(source, target):
            if oper == "==":
                if sfield == if_value:
                    self.tester.assertEqual(then_value, tfield)
                else:
                    self.tester.assertEqual(else_value, tfield)
            elif oper == "!'":
                if sfield != if_value:
                    self.tester.assertEqual(then_value, tfield)
                else:
                    self.tester.assertEqual(else_value, tfield)
            elif oper == "<":
                if sfield < if_value:
                    self.tester.assertEqual(then_value, tfield)
                else:
                    self.tester.assertEqual(else_value, tfield)
            elif oper == ">":
                if sfield > if_value:
                    self.tester.assertEqual(then_value, tfield)
                else:
                    self.tester.assertEqual(else_value, tfield)
            else:
                self.tester.assertIn(oper, ["==", "!=", "<", ">"])

    def test_domain_map(self, source, target, mappings):
        """
        Ensures the domain map pairings are correctly mapped in the target column
        :param self:
        :param source:
        :param target:
        :param mappings:
        :return:
        """
        for s, t in zip(source, target):
            if s in mappings:
                self.tester.assertEqual(mappings[s] == t)

    def test_xml(self):
        """
        Tests to see that the newly created xml file is equal to a pre-determined correct file
        :return:
        """
        out_xml = ET.parse(self.outXML).getroot()
        correct_xml = ET.parse(self.correctXML).getroot()
        self.tester.assertTrue(xml_compare(out_xml, correct_xml))

    def main(self):
        """
        Runs all of the tests for the specified object
        :return:
        """
        self.test_length()
        self.test_fields()
        if self.testObject.title == "CreateConfig":
            self.test_data()
            self.test_xml()
        elif self.testObject.title in ["Preview", "Stage", "Append"]:
            self.test_data()
        elif self.testObject.title == "Replace":
            self.test_replace_data()


class SourceTargetParser(object):
    """
    Class designed to store the essential parts of the xml file in readable python data structrues
    """

    def __init__(self, xml_file):
        self.xmlLocation = xml_file
        self.xml = ET.parse(self.xmlLocation).getroot()
        self.targetFields = []
        self.methods = _XMLMethodNames  # not actually the methods in this file, just the naming syntax for the xml
        self.Data = dict()
        self.parse()

    @functools.lru_cache()
    def get_sourcefields(self):
        """
        Returns and caches the source names as specified in the xml. Some might be None if there is no mapping to the
        corresponding target field.
        :return:
        """
        sourcefields = []
        fields = self.xml.find('Fields').getchildren()
        for field in fields:
            sourceName = field.find('SourceName').text
            sourcefields.append(sourceName)
        return sourcefields

    @functools.lru_cache()
    def get_targetfields(self):
        """
        Returns and caches the target field names as specified in the xml.
        :return:
        """
        targetfields = []
        fields = self.xml.find('Fields').getchildren()
        for field in fields:
            targetName = field.find('TargetName').text
            targetfields.append(targetName)
        return targetfields

    @functools.lru_cache()
    def get_pairings(self) -> dict:
        """
        Returns a dictionary where key is TargetName and value is SourceName for each field
        :return: dict
        """
        pairings = dict()
        fields = self.xml.find('Fields').getchildren()
        for field in fields:
            sourcename = field.find('SourceName').text
            targetname = field.find('TargetName').text
            pairings[targetname] = sourcename

    @functools.lru_cache()
    def get_methods(self):
        """
        Returns and caches the methods in order of appearence in the xml file.
        :return:
        """
        method_dict = dict()
        fields = self.xml.find('Fields').getchildren()
        for field in fields:
            targetname = field.find('TargetName').text
            method = field.find('Method').text
            method_dict[targetname] = method
        return method_dict

    @functools.lru_cache()
    def parse_replace(self) -> dict:
        """
        Returns a dictionary with the information used by Replace By Field Value
        :return: dict
        """
        replace_by = self.xml.find('ReplaceBy')
        outdict = dict()
        outdict["FieldName"] = replace_by.find('FieldName').text
        outdict['Operator'] = replace_by.find('Operator').text
        outdict['Value'] = replace_by.find('Value').text

        return outdict

    def parse(self):
        """
        Interprets the xml file and stores the information in appropriate places
        :return:
        """
        fields = self.xml.find('Fields').getchildren()
        for field in fields:
            targetName = field.find('TargetName').text
            sourceName = field.find('SourceName').text
            method = field.find('Method').text  # added for visibility

            self.targetFields.append(targetName)
            self.sourceFields.append(sourceName)
            self.methodList.append(method)

            if method == self.methods["Set Value"]:
                self.Data[targetName][self.methods["Set Value"]] = field.find(self.methods["Set Value"]).text
            elif method == self.methods["Domain Map"]:  # TODO: might want to review this. maybe will work, maybe won't
                DomainMap = field.find(self.methods["Domain Map"]).getchildren()
                for tag in DomainMap:
                    if tag.tag == "sValue":
                        svalue = tag.text
                    if tag.tag == "tValue":
                        self.Data[targetName][self.methods["Domain Map"]][svalue] = tag.text
                        svalue = ""
            elif method == self.methods["Value Map"]:
                ValueMap = field.find(self.methods["value Map"]).getchildren()
                for tag in ValueMap:
                    if tag.tag == "sValue":
                        svalue = tag.text
                    elif tag.tag == "tValue":
                        self.Data[targetName][self.methods["Value Map"]][svalue] = tag.text
                        svalue = ""
                    elif tag.tag == "Otherwise":
                        self.Data[targetName]["Otherwise"] = tag.text
            elif method == self.methods["Change Case"]:
                self.Data[targetName][self.methods["Change Case"]] = field.find(self.method["Change Case"]).text
            elif method == self.methods["Concatenate"]:
                self.Data[targetName]["Separator"] = field.find("Separator").text
                cfields = field.find("cfields").getchildren()
                for cfield in cfields:
                    self.Data[targetName][self.methods["Concatenate"]].append(cfield.find('Name').text)
            elif method == self.methods["Left"]:
                self.Data[targetName][self.methods["Left"]] = int(field.find(self.methods["Left"]).text)
            elif method == self.methods["Right"]:
                self.Data[targetName][self.methods["Right"]] = int(field.find(self.methods["Right"]).text)
            elif method == self.methods["Substring"]:
                self.Data[targetName]["Start"] = int(field.find('Start').text)
                self.Data[targetName]["Length"] = int(field.find('Length').text)
            elif method == self.methods["Split"]:
                self.Data[targetName]["SplitAt"] = field.find("SplitAt").text
                self.Data[targetName]["Part"] = int(field.find("Part").text)
            elif method == self.methods["Conditional Value"]:
                self.Data[targetName]["Oper"] = field.find("Oper").text.strip("\'").strip("\"")
                self.Data[targetName]["If"] = field.find("If").text.strip("\'").strip("\"")
                self.Data[targetName]["Then"] = field.find("Then").text.strip("\'").strip("\"")
                self.Data[targetName]["Else"] = field.find("Else").text.strip("\'").strip("\"")
            else:
                assert method in self.methods.values()
