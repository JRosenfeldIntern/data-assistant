import unittest
import os, sys
import arcpy
import pathlib
from inc_datasources import _daGPTools, _dbConnStr, _layerFiles, _configMatrix, _validConfigFiles, \
    _invalidConfigFiles, _localOutputPath

sys.path.insert(0, _daGPTools)
import test_CreateConfigFile, test_dlaPreview, test_dlaStage

if __name__ == '__main__':
    suite = unittest.TestSuite()
    #suite.addTest(test_CreateConfigFile.TestCreateConfigWorkflows("test_CreateConfig"))

   # suite.addTest(test_dlaPreview.TestPreview("test_preview"))
   # suite.addTest(test_dlaPreview.TestPreview("testFields"))
   # suite.addTest(test_dlaPreview.TestPreview("testData"))
   # suite.addTest(test_dlaPreview.TestPreview("testLength"))

    suite.addTest(test_dlaStage.TestStaging("test_stage"))
   # suite.addTest(test_dlaStage.TestStaging("testFields"))
    #suite.addTest(test_dlaStage.TestStaging("testData"))
    #suite.addTest(test_dlaStage.TestStaging("testLength"))

    runner = unittest.TextTestRunner()

    for testCase in _configMatrix:
        xmlLocation = testCase["xmlLocation"]
        results = runner.run(suite)
    # check the test and if there are failures, write to disk
    if len(results.failures) > 0:
        for fail in results.failures:
            with open(os.path.join(_localOutputPath, "Failed_ExportDataset.txt"), "w") as text_file:
                print(fail, file=text_file)
    else:
        print("No failures")