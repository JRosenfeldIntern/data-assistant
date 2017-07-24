import sys
import unittest

import create
from inc_datasources import _daGPTools, _configMatrix, _localWorkspace, _outputDirectory

sys.path.insert(0, _daGPTools)
import dlaTesterFunctions as tf
from dlaTesterFunctions import Helper


#
# if __name__ == '__main__':
# 	createConfig = test_CreateConfigFile.TestCreateConfigWorkflows()
# 	preview = test_dlaPreview.TestPreview()
# 	stage = test_dlaStage.TestStaging()
# 	append = test_dlaAppend.TestAppend()
# 	replace = test_dlaReplace.TestReplace()
#
# 	for testCase, lw in zip(_configMatrix, _localWorkspace):
# 		suite = unittest.TestSuite()
# 		suite.addTest(createConfig.run_test(testCase, lw))
# 		#suite.addTest(preview.run_test(testCase, lw))
# 		suite.addTest(append.run_test(testCase, lw))
# 		#suite.addTest(replace.run_test(testCase,lw))
# 		#suite.addTest(stage.run_test(testCase, lw))
#
# 		runner = unittest.TextTestRunner()
# 		runner.run(suite)


class UnitTests(unittest.TestCase):
    """
    Runs the unit tests for the various functions for all test cases and data sources
    """

    def setUp(self):
        tf.clear_feature_classes(_outputDirectory)
        pass

    def tearDown(self):
        tf.restore_data()
        pass

    def main(self):
        """
        Performs the tests while iterating through test cases
        :return: None
        """
        for test_case, local_workspace in zip(_configMatrix, _localWorkspace):
            suite = unittest.TestCase()
            create_config = create.CreateConfig(local_workspace, test_case)
            preview = create.Preview(local_workspace, test_case)  # optional parameter to set row limit
            stage = create.Stage(local_workspace, test_case)
            append = create.Append(local_workspace, test_case)
            replace = create.Replace(local_workspace, test_case)

            configTest = Helper(self, create_config, local_workspace, test_case)
            previewTest = Helper(self, preview, local_workspace, test_case)
            stageTest = Helper(self, stage, local_workspace, test_case)
            appendTest = Helper(self, append, local_workspace, test_case)
            replace = Helper(self, replace, local_workspace, test_case)

            # configTest.run_tests()                One or the other between these two, not sure yet
            # runner.addTest(configTest.run_tests())


if __name__ == '__main__':
    test = UnitTests()
    test.main()
