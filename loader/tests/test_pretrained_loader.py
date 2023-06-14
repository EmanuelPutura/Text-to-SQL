from unittest import TestCase, mock
import json
import os
import shutil

from loader.pretrained_loader import get_all_pretrained_models_dir_names, get_pretrained_model_metadata_from_dir, get_all_pretrained_models_metadata


class TestWikiSQLFormatter(TestCase):
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    TEST_PRETRAINED_DIR = 'test_pretrained'
    METADATA_FILE_NAME = 'metadata.json'

    METADATA = {
        "name": "PretrainedModel",
        "version": "1.0",
        "class_name": "SQLCodeT5Baseline",
        "base_mode": "NOT DEFINED",
        "results": {
            "wikisql_acc": {
            },
            "rouge": {
            }
        },
        "other_information": "NA"
    }

    def setUp(self):
        os.makedirs(self.TEST_PRETRAINED_DIR)
        metadata_path = os.path.join(self.TEST_PRETRAINED_DIR, self.METADATA_FILE_NAME)

        # Open the file in write mode and write the JSON data
        with open(metadata_path, "w+") as json_file:
            json.dump(self.METADATA, json_file)

    def tearDown(self):
        shutil.rmtree(self.TEST_PRETRAINED_DIR)

    def test_get_all_pretrained_models_dir_names(self):
        with mock.patch('loader.pretrained_loader.PRETRAINED_MODELS_PATH', self.CURRENT_DIR):
            assert get_all_pretrained_models_dir_names() == [self.TEST_PRETRAINED_DIR]

    def test_get_pretrained_model_metadata_from_dir(self):
        with mock.patch('loader.pretrained_loader.PRETRAINED_MODELS_PATH', self.CURRENT_DIR):
            assert get_pretrained_model_metadata_from_dir(self.TEST_PRETRAINED_DIR) == self.METADATA

    def test_get_all_pretrained_models_metadata(self):
        with mock.patch('loader.pretrained_loader.PRETRAINED_MODELS_PATH', self.CURRENT_DIR):
            assert get_all_pretrained_models_metadata() == {self.TEST_PRETRAINED_DIR: self.METADATA}
