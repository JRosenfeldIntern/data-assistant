import unittest
import os, sys
import arcpy
import pathlib
from inc_datasources import _daGPTools, _dbConnStr, _configMatrix, _validConfigFiles, \
	_invalidConfigFiles, _localOutputPath

sys.path.insert(0, _daGPTools)
import dlaCreateSourceTarget, dla, dlaStage


def importUtilNetworkToolbox():
	parentPath = os.path.join(str(pathlib.Path(__file__).parents[1]), 'UtilityNetworkConfigurationTools')
	python_toolbox = os.path.join(parentPath, 'UtilityNetworkConfigurationTools.pyt')
	sys.path.insert(0, parentPath)
	if sys.version_info[:2] >= (3, 5):
		# import importlib.util
		# spec = importlib.util.spec_from_file_location("UtilityNetworkSchemaTools.pyt", parentPath)
		# return importlib.util.module_from_spec(spec)
		import types
		from importlib.machinery import SourceFileLoader
		loader = SourceFileLoader("UtilityNetworkConfigurationTools", python_toolbox)
		pyt = types.ModuleType(loader.name)
		loader.exec_module(pyt)
		return pyt
	elif sys.version_info[:2] >= (3, 4):
		import types
		from importlib.machinery import SourceFileLoader
		loader = SourceFileLoader("UtilityNetworkConfigurationTools", python_toolbox)
		pyt = types.ModuleType(loader.name)
		loader.exec_module(pyt)
		return pyt
	elif sys.version_info[:2] >= (3, 3):
		from importlib.machinery import SourceFileLoader
		return SourceFileLoader('UtilityNetworkConfigurationTools', python_toolbox).load_module()
	else:
		import imp
		return imp.load_source('UtilityNetworkConfigurationTools', python_toolbox)


class TestCreateConfigWorkflows(unittest.TestCase):
	cleanup = True

	def setUp(self):
		# self.assertTrue(arcpy.Exists(_dbConnStr[0]["sdePath"]))
		# self._utilNetworkToolboxModule = importUtilNetworkToolbox()
		pass

	def tearDown(self):
		# if cleanup == True:
		# if arcpy.Exists(os.path.join(_localOutputPath,_dbConnStr[0]["domain"]+".gdb")):
		# os.remove(os.path.join(_localOutputPath,_dbConnStr[0]["domain"]+".gdb"))
		pass

	def test_CreateConfig(self):
		sourcePath = dla.getLayerPath(testCase["Source"]["dataPath"])
		targetPath = dla.getLayerPath(testCase["Target"]["dataPath"])
		self.assertTrue(dlaCreateSourceTarget.createDlaFile(sourcePath, targetPath, xmlLocation))


if __name__ == '__main__':
	# suite = unittest.TestSuite()
	suite = unittest.TestSuite()
	#runner = unittest.TextTestRunner()
	runner = unittest.TextTestRunner()
	for testCase in _configMatrix:
		xmlLocation = testCase["xmlLocation"]
		suite.addTest(TestCreateConfigWorkflows("test_CreateConfig"))
	results = runner.run(suite)
# check the test and if there are failures, write to disk
if len(results.failures) > 0:
	for fail in results.failures:
		with open(os.path.join(_localOutputPath, "Failed_ExportDataset.txt"), "w") as text_file:
			print(fail, file=text_file)
else:
	print("No failures")
