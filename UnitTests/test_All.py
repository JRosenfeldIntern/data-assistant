import sys
import unittest

import create
from inc_datasources import _daGPTools, _configMatrix, _localWorkspace, _outputDirectory
import dlaTesterFunctions as tf
from dlaTesterFunctions import Helper

sys.path.insert(0, _daGPTools)


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
            suite = unittest.TestSuite()
            runner = unittest.TextTestRunner()

            create_config = create.CreateConfig(local_workspace, test_case)
            preview = create.Preview(local_workspace, test_case)  # optional parameter to set row limit
            stage = create.Stage(local_workspace, test_case)
            append = create.Append(local_workspace, test_case)
            replace = create.Replace(local_workspace, test_case)

            config_test = Helper(self, create_config, local_workspace, test_case)
            preview_test = Helper(self, preview, local_workspace, test_case)
            stage_test = Helper(self, stage, local_workspace, test_case)
            append_test = Helper(self, append, local_workspace, test_case)
            replace_test = Helper(self, replace, local_workspace, test_case)

            suite.addTest(config_test.main())
            suite.addTest(preview_test.main())
            suite.addTest(stage_test.main())
            suite.addTest(append_test.main())
            suite.addTest(replace_test.main())

            results = runner.run(suite)


if __name__ == '__main__':
    test = UnitTests()
    test.main()
