import os
import shutil

import arcpy

import dla
import dlaCreateSourceTarget
import dlaPreview
import dlaPublish
import dlaStage
import dlaTesterFunctions
from inc_datasources import _outputDirectory
import dla


class BaseClass(object):
    """
    Class used for inheritance that contains basic common information
    """
    def __init__(self, lw, tc):
        self.localWorkspace = lw
        self.TestCase = tc
        self.xmlLocation = tc["xmlLocation"]
        self.globalIDCheck = dla.processGlobalIds(dla.getXmlDoc(self.xmlLocation))
        self.title = self.__class__.__name__


class CreateConfig(BaseClass):
    """
    A class that is designed to create and house information to test dlaCreateSourceTarget
    """

    def __init__(self, lw, tc):
        super().__init__(lw, tc)

    # def importUtilNetworkToolbox():
    #     parentPath = os.path.join(str(pathlib.Path(__file__).parents[1]), 'UtilityNetworkConfigurationTools')
    #     python_toolbox = os.path.join(parentPath, 'UtilityNetworkConfigurationTools.pyt')
    #     sys.path.insert(0, parentPath)
    #     if sys.version_info[:2] >= (3, 5):
    #         # import importlib.util
    #         # spec = importlib.util.spec_from_file_location("UtilityNetworkSchemaTools.pyt", parentPath)
    #         # return importlib.util.module_from_spec(spec)
    #         import types
    #         from importlib.machinery import SourceFileLoader
    #         loader = SourceFileLoader("UtilityNetworkConfigurationTools", python_toolbox)
    #         pyt = types.ModuleType(loader.name)
    #         loader.exec_module(pyt)
    #         return pyt
    #     elif sys.version_info[:2] >= (3, 4):
    #         import types
    #         from importlib.machinery import SourceFileLoader
    #         loader = SourceFileLoader("UtilityNetworkConfigurationTools", python_toolbox)
    #         pyt = types.ModuleType(loader.name)
    #         loader.exec_module(pyt)
    #         return pyt
    #     elif sys.version_info[:2] >= (3, 3):
    #         from importlib.machinery import SourceFileLoader
    #         return SourceFileLoader('UtilityNetworkConfigurationTools', python_toolbox).load_module()
    #     else:
    #         import imp
    #         return imp.load_source('UtilityNetworkConfigurationTools', python_toolbox)

    def main(self):
        """
        Runs the initial action of the test and returns it
        :return: boolean
        """
        source_path = dla.getLayerPath(os.path.join(self.localWorkspace["Source"], self.localWorkspace["SourceName"]))
        target_path = dla.getLayerPath(os.path.join(self.xmlLocation["Target"], self.localWorkspace["TargetName"]))
        field_matcher = os.path.dirname(os.path.realpath(__file__))
        shutil.copy(self.TestCase["MatchLibrary"], field_matcher)
        return dlaCreateSourceTarget.createDlaFile(source_path, target_path, self.xmlLocation)


class Preview(BaseClass):
    """
    A class that is designed to create and house information to test dlaPreview
    """

    def __init__(self, lw, tc, rl=100):
        super().__init__(lw, tc)
        self.rowLimit = rl

    def main(self):
        """
        Creates a preview feature class in dla.gdb for testing
        :return: None or False
        """
        dlaPreview.rowLimit = self.rowLimit
        return dlaPreview.preview(self.xmlLocation)  # creates the new feature class


class Stage(BaseClass):
    """
    A class that is designed to create and house information to test dlaStage
    """

    def __init__(self, lw, tc):
        super().__init__(lw, tc)

    def main(self):
        """
        Creates a staged version of the code in a feature class in dla.gdb for testing
        :return: None or False
        """
        return dlaStage.stage(self.xmlLocation)  # creates the new feature class


class Append(BaseClass):
    """
    A class that is designed to create and house information to test dlaAppend
    """

    def __init__(self, lw: dict, tc: dict):
        super().__init__(lw, tc)
        self.directory = _outputDirectory

    def main(self):
        """
        Creates a copy of the target data and saves it to a feature class in dla.gdb. It then appends data
        onto the end of target for testing
        :return:
        """
        dlaTesterFunctions.make_copy(self.directory)
        dlaPublish._useReplaceSettings = False
        return dlaPublish.publish(self.xmlLocation)


class Replace(BaseClass):
    """
    A class that is designed to create and house information to test dlaReplaceByField
    """

    def __init__(self, lw: dict, tc: dict):
        super().__init__(lw, tc)
        self.directory = _outputDirectory

    def main(self):
        """
        Applys the ReplaceByField operation specified in the xml file to the data for testing
        :return: None or False
        """
        dlaTesterFunctions.make_copy(self.directory)
        dlaPublish._useReplaceSettings = True
        return dlaPublish.publish(self.xmlLocation)
