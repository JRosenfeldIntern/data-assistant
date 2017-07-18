import unittest
import os, sys
import arcpy
import pathlib
from inc_datasources import _daGPTools, _dbConnStr,  _configMatrix, _validConfigFiles, _invalidConfigFiles, \
	_localOutputPath, _localWorkspace, _outputDirectory

sys.path.insert(0, _daGPTools)
import dla, dlaStage, dlaCreateSourceTarget, dlaTesterFunctions, dlaPublish


class TestAppend(unittest.TestCase):
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

	def make_copy(self):
		directory = _outputDirectory
		dlaTesterFunctions.clearFeatureClasses(directory) # creating a copy of the target feature class
		arcpy.env.workspace = localWorkspace["Target"] # to compare to after append
		arcpy.CopyFeatures_management("Target",os.path.join(directory,"copy"))

	def test_append(self):
		self.make_copy()
		dlaPublish._useReplaceSettings = False
		self.assertIsNone(dlaPublish.publish(xmlLocation))

	def testFields(self):
		directory = _outputDirectory
		dlaTesterFunctions.test_fields(self,directory,localWorkspace,xmlLocation)

	def testData(self):
		sourceFCPath = localWorkspace["Source"]
		arcpy.env.workspace = sourceFCPath
		sourceFeatureClass = ""
		for fc in arcpy.ListFeatureClasses():
			if fc == "source":
				sourceFeatureClass = fc
		sourceDataPath = os.path.join(sourceFCPath,sourceFeatureClass)


		targetFCPath = localWorkspace["Target"]
		arcpy.env.workspace = targetFCPath
		targetFeatureClass = ""
		for fc in arcpy.ListFeatureClasses():
			if fc == "Target":
				targetFeatureClass = fc


		fields = [dla.getNodeValue(field,"TargetName") for field in dla.getXmlElements(_configMatrix[0]["xmlLocation"],"Field")]
		try:
			fields.remove("GLOBALID") #TODO: remove or fix. very conditional to the specific data set
		except:
			None
		targetDataPath = os.path.join(targetFCPath,targetFeatureClass)
		targetCursor = dlaTesterFunctions.build_table(targetFCPath,targetFeatureClass)

		directory = _outputDirectory
		copyDataPath = os.path.join(directory,"copy")

		targetCursor = [row for row in arcpy.da.SearchCursor(targetDataPath,fields)]
		copyCursor = [row for row in arcpy.da.SearchCursor(copyDataPath,fields)]

		for origin,copy in zip(targetCursor,copyCursor):
			self.assertEqual(origin,copy)

		dlaTesterFunctions.test_data(self, sourceDataPath , targetDataPath, xmlLocation,len(copyCursor), True)


	def testLength(self):
		dlaTesterFunctions.test_length(tester=self, mode="Append", localWorkspace = localWorkspace)

	def run_test(self,testCase,lw):
		suite = unittest.TestSuite()
		runner = unittest.TextTestRunner()

		global xmlLocation
		xmlLocation = testCase["xmlLocation"]
		global localWorkspace
		localWorkspace = lw
		suite.addTest(TestAppend("test_append"))
		suite.addTest(TestAppend("testData"))
		suite.addTest(TestAppend("testLength"))
		suite.addTest(TestAppend("testFields"))

		directory = _outputDirectory
		copyDataPath = os.path.join(directory, "copy")
		targetDataPath = os.path.join(localWorkspace["Target"], localWorkspace["TargetName"])
		dlaTesterFunctions.restoreFeatureClass(copyDataPath, targetDataPath)
		results = runner.run(suite)

		# check the test and if there are failures, write to disk
		if len(results.failures) > 0:
			for fail in results.failures:
				with open(os.path.join(_localOutputPath, "Failed_ExportDataset.txt"), "w") as text_file:
					print(fail, file=text_file)
		else:
			print("No failures")
if __name__ == '__main__':
	TestAppend.run_test(_configMatrix[0],_localWorkspace[0])
