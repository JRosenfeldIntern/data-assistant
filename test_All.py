import unittest
import os, sys
import arcpy
import pathlib
from inc_datasources import _daGPTools, _dbConnStr, _configMatrix, _validConfigFiles, \
	_invalidConfigFiles, _localOutputPath, _localWorkspace

sys.path.insert(0, _daGPTools)
import test_CreateConfigFile, test_dlaPreview, test_dlaStage, test_dlaAppend, test_dlaReplace

if __name__ == '__main__':
	createConfig = test_CreateConfigFile.TestCreateConfigWorkflows()
	preview = test_dlaPreview.TestPreview()
	stage = test_dlaStage.TestStaging()
	append = test_dlaAppend.TestAppend()
	replace = test_dlaReplace.TestReplace()

	for testCase, lw in zip(_configMatrix, _localWorkspace):
		suite = unittest.TestSuite()
		suite.addTest(createConfig.run_test(testCase, lw))
		suite.addTest(preview.run_test(testCase, lw))
		suite.addTest(append.run_test(testCase, lw))
		suite.addTest(stage.run_test(testCase, lw))
		suite.addTest(replace.run_test(testCase,lw))

		runner = unittest.TextTestRunner()
		runner.run(suite)
