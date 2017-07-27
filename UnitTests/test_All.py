import sys
import unittest

import create
import dlaTesterFunctions as tf
from dlaTesterFunctions import Helper
from inc_datasources import _daGPTools, _configMatrix, _localWorkspace, _outputDirectory

sys.path.insert(0, _daGPTools)


class UnitTests(object):
    """
    Runs the unit tests for the various functions for all test cases and data sources
    """

    def main(self):
        """
        Performs the tests while iterating through test cases
        :return: None
        """
        for test_case, local_workspace in zip(_configMatrix, _localWorkspace):
            runner = unittest.TextTestRunner()

            create_config = create.CreateConfig(local_workspace, test_case)
            preview = create.Preview(local_workspace, test_case)  # optional parameter to set row limit
            stage = create.Stage(local_workspace, test_case)
            append = create.Append(local_workspace, test_case)
            replace = create.Replace(local_workspace, test_case)


            tf.clear_feature_classes(_outputDirectory)
            config_test = Helper(create_config, local_workspace, test_case)
            preview_test = Helper(preview, local_workspace, test_case)
            stage_test = Helper(stage, local_workspace, test_case)
            append_test = Helper(append, local_workspace, test_case)
            replace_test = Helper(replace, local_workspace, test_case)


            results = runner.run(suite)
        tf.restore_data()


if __name__ == '__main__':
    test = UnitTests()
    test.main()
