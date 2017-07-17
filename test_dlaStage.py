import unittest
import os,sys
import arcpy
import pathlib
from inc_datasources import _daGPTools, _dbConnStr, _configMatrix, _validConfigFiles, _invalidConfigFiles, _localOutputPath, _localWorkspace
sys.path.insert(0, _daGPTools)
import dla,dlaStage, dlaCreateSourceTarget, dlaTesterFunctions


class TestStaging(unittest.TestCase):
    cleanup = True
    def setUp(self):      
        #self.assertTrue(arcpy.Exists(_dbConnStr[0]["sdePath"]))
        #self._utilNetworkToolboxModule = importUtilNetworkToolbox()
        pass

    def tearDown(self):
        #if cleanup == True:
            #if arcpy.Exists(os.path.join(_localOutputPath,_dbConnStr[0]["domain"]+".gdb")):
                #os.remove(os.path.join(_localOutputPath,_dbConnStr[0]["domain"]+".gdb"))
        pass

    def test_stage(self):
	    directory = r"C:\Users\josh9173\Documents\DataAssistantTests\unitTest\dla.gdb"
	    arcpy.env.workspace = directory
	    dlaTesterFunctions.clearFeatureClasses(directory)
	    dlaStage.stage(xmlLocation)

    def testFields(self):
	    directory = r"C:\Users\josh9173\Documents\DataAssistantTests\unitTest\dla.gdb"
	    dlaTesterFunctions.test_fields(self,directory,localWorkspace,xmlLocation)

    def testData(self):
	    sourceFCPath = localWorkspace["Source"]
	    sourceDataPath = os.path.join(sourceFCPath, "source")

	    directory = r"C:\Users\josh9173\Documents\DataAssistantTests\unitTest\dla.gdb"
	    arcpy.env.workspace = directory
	    featureclass = arcpy.ListFeatureClasses()[0]
	    localDataPath = os.path.join(directory, featureclass)

	    dlaTesterFunctions.test_data(self, sourceDataPath,localDataPath,xmlLocation)

    def testLength(self):
	    dlaTesterFunctions.test_length(tester = self, mode = "Stage", localWorkspace = localWorkspace)

if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestStaging("test_stage"))
	suite.addTest(TestStaging("testFields"))
	suite.addTest(TestStaging("testData"))
	suite.addTest(TestStaging("testLength"))
	runner = unittest.TextTestRunner()
	for testCase,lw in zip(_configMatrix,_localWorkspace):
		xmlLocation = testCase["xmlLocation"]
		localWorkspace = lw
		results = runner.run(suite)
	# check the test and if there are failures, write to disk
	if len(results.failures) > 0:
		for fail in results.failures:
			with open(os.path.join(_localOutputPath, "Failed_ExportDataset.txt"), "w") as text_file:
				print(fail, file=text_file)
	else:
		print("No failures")