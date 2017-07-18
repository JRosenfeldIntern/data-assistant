import unittest
import os, sys
import arcpy
import pathlib
from inc_datasources import _daGPTools, _dbConnStr, _configMatrix, _validConfigFiles, _invalidConfigFiles, \
	_localOutputPath, \
	_localWorkspace, _outputDirectory

sys.path.insert(0, _daGPTools)
import dla, dlaStage, dlaCreateSourceTarget, dlaTesterFunctions


class TestStaging(unittest.TestCase):
	cleanup = True
	localWorkspace = []
	xmlLocation = ""

	def setUp(self):
		# self.assertTrue(arcpy.Exists(_dbConnStr[0]["sdePath"]))
		# self._utilNetworkToolboxModule = importUtilNetworkToolbox()
		pass

	def tearDown(self):
		# if cleanup == True:
		# if arcpy.Exists(os.path.join(_localOutputPath,_dbConnStr[0]["domain"]+".gdb")):
		# os.remove(os.path.join(_localOutputPath,_dbConnStr[0]["domain"]+".gdb"))
		pass

	def test_stage(self):
		directory = _outputDirectory
		arcpy.env.workspace = directory
		dlaTesterFunctions.clearFeatureClasses(directory)
		dlaStage.stage(xmlLocation)

	def testFields(self):
		directory = _outputDirectory
		dlaTesterFunctions.test_fields(self, directory, localWorkspace, xmlLocation)

	def testData(self):
		sourceFCPath = localWorkspace["Source"]
		sourceDataPath = os.path.join(sourceFCPath, "source")

		directory = _outputDirectory
		arcpy.env.workspace = directory
		featureclass = arcpy.ListFeatureClasses()[0]
		localDataPath = os.path.join(directory, featureclass)

		dlaTesterFunctions.test_data(self, sourceDataPath, localDataPath, xmlLocation)

	def testLength(self):
		dlaTesterFunctions.test_length(tester=self, mode="Stage", localWorkspace=localWorkspace)

	def run_test(self, testCase, lw):
		suite = unittest.TestSuite()
		runner = unittest.TextTestRunner()
		global xmlLocation
		xmlLocation = testCase["xmlLocation"]
		global localWorkspace
		localWorkspace = lw
		suite.addTest(TestStaging("test_stage"))
		suite.addTest(TestStaging("testFields"))
		suite.addTest(TestStaging("testData"))
		suite.addTest(TestStaging("testLength"))
		return suite
		#results = runner.run(suite)

		# check the test and if there are failures, write to disk
		if len(results.failures) > 0:
			for fail in results.failures:
				with open(os.path.join(_localOutputPath, "Failed_ExportDataset.txt"), "w") as text_file:
					print(fail, file=text_file)
		else:
			print("No failures")


if __name__ == '__main__':
	TestStaging.run_test(_configMatrix[0], _localWorkspace[0])
