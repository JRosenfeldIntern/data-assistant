import unittest
import os, sys
import arcpy
import pathlib
from inc_datasources import _daGPTools, _dbConnStr,_configMatrix,_localWorkspace, _outputDirectory

sys.path.insert(0, _daGPTools)
import dla, dlaPreview, dlaCreateSourceTarget, dlaFieldCalculator, dlaTesterFunctions


class TestPreview(unittest.TestCase):
	cleanup = True
	rowLim = 200
	localWorkspace = []
	xmlLocation = ""

	def setUp(self): #supposed to run before every test
		# self.assertTrue(arcpy.Exists(_dbConnStr[0]["sdePath"]))
		# self._utilNetworkToolboxModule = importUtilNetworkToolbox()
		pass

	def tearDown(self):
		# if cleanup == True:
		# if arcpy.Exists(os.path.join(_localOutputPath,_dbConnStr[0]["domain"]+".gdb")):
		# os.remove(os.path.join(_localOutputPath,_dbConnStr[0]["domain"]+".gdb"))
		pass

	def test_preview(self):
		directory = _outputDirectory
		arcpy.env.workspace = directory
		dlaTesterFunctions.clearFeatureClasses(directory)
		dlaPreview.rowLimit = self.rowLim
		dlaPreview.preview(xmlLocation) #creates the new feature class

	def testFields(self):
		directory = _outputDirectory
		dlaTesterFunctions.test_fields(self,directory,localWorkspace,xmlLocation)

	def testData(self):
		sourceFCPath = localWorkspace["Source"]
		sourceDataPath = os.path.join(sourceFCPath,localWorkspace["SourceName"])

		directory = _outputDirectory
		arcpy.env.workspace = directory
		featureclass = arcpy.ListFeatureClasses()[0]
		localDataPath = os.path.join(directory,featureclass)

		dlaTesterFunctions.test_data(self,sourceDataPath,localDataPath,xmlLocation)

	def testLength(self): #Testing multiple lengths would require recreating the preview file. Should that be done?
		sourceFCPath = localWorkspace["Source"]
		sourceCursor = dlaTesterFunctions.build_table(sourceFCPath,localWorkspace["SourceName"])
		count = len(sourceCursor)
		if count < self.rowLim:
			dlaTesterFunctions.test_length(tester = self, mode = "Preview",localWorkspace = localWorkspace ,rowLimit = count)
		else:
			dlaTesterFunctions.test_length(tester = self,mode = "Preview",localWorkspace = localWorkspace,rowLimit = self.rowLim)

	def run_test(self,testCase,lw):
		suite = unittest.TestSuite()
		runner = unittest.TextTestRunner()
		global xmlLocation
		xmlLocation = testCase["xmlLocation"]
		global localWorkspace
		localWorkspace = lw
		suite.addTest(TestPreview("test_preview"))
		suite.addTest(TestPreview("testFields"))
		suite.addTest(TestPreview("testData"))
		suite.addTest(TestPreview("testLength"))
		results = runner.run(suite)
		# check the test and if there are failures, write to disk
		if len(results.failures) > 0:
			for fail in results.failures:
				with open(os.path.join(_localOutputPath, "Failed_ExportDataset.txt"), "w") as text_file:
					print(fail, file=text_file)
		else:
			print("No failures")

if __name__ == '__main__':
	run_test(self,_configMatrix[0],_localWorkspace[0])
