import unittest
import os, sys
import arcpy
import pathlib
from inc_datasources import _daGPTools, _dbConnStr, _configMatrix, _validConfigFiles, _invalidConfigFiles, \
	_localOutputPath, _localWorkspace, _outputDirectory

sys.path.insert(0, _daGPTools)
import dla, dlaStage, dlaCreateSourceTarget, dlaTesterFunctions, dlaPublish


class TestReplace(unittest.TestCase):
	cleanup = True
	xmlLocation = ""
	localWorkspace = []

	def setUp(self):
		# self.assertTrue(arcpy.Exists(_dbConnStr[0]["sdePath"]))
		# self._utilNetworkToolboxModule = importUtilNetworkToolbox()
		pass

	def tearDown(self):
		# if cleanup == True:
		# if arcpy.Exists(os.path.join(_localOutputPath,_dbConnStr[0]["domain"]+".gdb")):
		# os.remove(os.path.join(_localOutputPath,_dbConnStr[0]["domain"]+".gdb"))
		pass

	def make_copy(self):
		directory = _outputDirectory
		dlaTesterFunctions.clearFeatureClasses(directory)  # creating a copy of the target feature class
		arcpy.env.workspace = localWorkspace["Target"]  # to compare to after append
		arcpy.CopyFeatures_management("Target", os.path.join(directory, "copy"))

	def test_replace(self):
		self.make_copy()
		dlaPublish._useReplaceSettings = True
		self.assertIsNone(dlaPublish.publish(xmlLocation))

	def testFields(self):
		directory = _outputDirectory
		dlaTesterFunctions.test_fields(self, directory, localWorkspace, xmlLocation)

	def testData(self):
		sourceFCPath = localWorkspace["Source"]
		sourceFeatureClass = localWorkspace["SourceName"]
		sourceDataPath = os.path.join(sourceFCPath, sourceFeatureClass)

		targetFCPath = localWorkspace["Target"]
		targetFeatureClass = localWorkspace["TargetName"]
		targetDataPath = os.path.join(targetFCPath, targetFeatureClass)

		copyDataPath = os.path.join(_outputDirectory,"copy")

		dlaTesterFunctions.test_replace_data(self, sourceDataPath, targetDataPath,copyDataPath, xmlLocation)

	def testLength(self):
		dlaTesterFunctions.test_length(tester=self, mode="Replace", localWorkspace=localWorkspace)

	def run_test(self, testCase, lw):
		suite = unittest.TestSuite()
		runner = unittest.TextTestRunner()
		global xmlLocation
		xmlLocation = testCase["xmlLocation"]
		global localWorkspace
		localWorkspace = lw
		suite.addTest(TestReplace("test_replace"))
		suite.addTest(TestReplace("testData"))
		suite.addTest(TestReplace("testLength"))
		suite.addTest(TestReplace("testFields"))

		#results = runner.run(suite)
		return suite
		# check the test and if there are failures, write to disk
		if len(results.failures) > 0:
			for fail in results.failures:
				with open(os.path.join(_localOutputPath, "Failed_ExportDataset.txt"), "w") as text_file:
					print(fail, file=text_file)
		else:
			print("No failures")


if __name__ == '__main__':
	replace = TestReplace()
	replace.run_test(_configMatrix[0], _localWorkspace[0])
