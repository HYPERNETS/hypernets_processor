"""
Tests for HypernetsDSBuilder class
"""

import unittest
from unittest.mock import patch
import random
import string
from hypernets_processor.test.test_functions import setup_test_context, teardown_test_context
from hypernets_processor.data_io.hypernets_ds_builder import HypernetsDSBuilder
from hypernets_processor.version import __version__


'''___Authorship___'''
__author__ = "Sam Hunt"
__created__ = "7/5/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class TestHypernetsDSBuilder(unittest.TestCase):

    @patch('hypernets_processor.data_io.hypernets_ds_builder.create_template_dataset')
    @patch('hypernets_processor.data_io.hypernets_ds_builder.ProductNameUtil')
    def test_create_ds_template_context(self, mock_pnu, mock_create_template_dataset):
        temp_name = ''.join(random.choices(string.ascii_lowercase, k=6))

        context = setup_test_context(anomoly_db_url="sqlite:///anomoly_"+temp_name+".db",
                                     metadata_db_url="sqlite:///metadata_"+temp_name+".db",
                                     create_dbs=True)
        dim_sizes_dict = {"n_w": 271, "n_s": 10}

        variables_dict_defs = {"def1": "vars1", "def2": "vars2"}
        metadata_defs = {"def1": {}, "def2": {}}

        hdsb = HypernetsDSBuilder(context=context,
                                  variables_dict_defs=variables_dict_defs,
                                  metadata_defs=metadata_defs)
        ds = hdsb.create_ds_template(dim_sizes_dict,
                                     ds_format="def1",
                                     propagate_ds="propagate_ds")

        # test calls to create_template_dataset
        mock_pnu.return_value.create_product_name.assert_called_once_with("def1", context=context)
        mock_create_template_dataset.assert_called_once_with("vars1", dim_sizes_dict,
                                                             metadata={"product_name":
                                                                mock_pnu.return_value.create_product_name.return_value},
                                                             propagate_ds="propagate_ds",
                                                             metadata_db=context.metadata_db,
                                                             metadata_db_query={})

        teardown_test_context(context, remove_dbs=True)

    @patch('hypernets_processor.data_io.hypernets_ds_builder.create_template_dataset')
    @patch('hypernets_processor.data_io.hypernets_ds_builder.ProductNameUtil')
    def test_create_ds_template_context_no_db(self, mock_pnu, mock_create_template_dataset):

        context = setup_test_context()

        dim_sizes_dict = {"n_w": 271, "n_s": 10}

        variables_dict_defs = {"def1": "vars1", "def2": "vars2"}
        metadata_defs = {"def1": {}, "def2": {}}

        hdsb = HypernetsDSBuilder(context=context,
                                  variables_dict_defs=variables_dict_defs,
                                  metadata_defs=metadata_defs)
        ds = hdsb.create_ds_template(dim_sizes_dict,
                                     ds_format="def1",
                                     propagate_ds="propagate_ds")

        # test calls to create_template_dataset
        mock_pnu.return_value.create_product_name.assert_called_once_with("def1", context=context)
        mock_create_template_dataset.assert_called_once_with("vars1", dim_sizes_dict,
                                                             metadata={"product_name":
                                                                mock_pnu.return_value.create_product_name.return_value},
                                                             propagate_ds="propagate_ds",
                                                             metadata_db=context.metadata_db,
                                                             metadata_db_query=None)

    @patch('hypernets_processor.data_io.hypernets_ds_builder.create_template_dataset')
    @patch('hypernets_processor.data_io.hypernets_ds_builder.ProductNameUtil')
    def test_create_ds_template_no_context(self, mock_pnu, mock_create_template_dataset):

        dim_sizes_dict = {"n_w": 271, "n_s": 10}

        variables_dict_defs = {"def1": "vars1", "def2": "vars2"}
        metadata_defs = {"def1": {}, "def2": {}}

        hdsb = HypernetsDSBuilder(variables_dict_defs=variables_dict_defs, metadata_defs=metadata_defs)
        ds = hdsb.create_ds_template(dim_sizes_dict, ds_format="def1", propagate_ds="propagate_ds")

        # test calls to create_template_dataset
        mock_pnu.return_value.create_product_name.assert_called_once_with("def1", context=None)
        mock_create_template_dataset.assert_called_once_with("vars1", dim_sizes_dict,
                                                             metadata={"product_name":
                                                                mock_pnu.return_value.create_product_name.return_value},
                                                             propagate_ds="propagate_ds",
                                                             metadata_db=None,
                                                             metadata_db_query=None)

    @patch('hypernets_processor.data_io.hypernets_ds_builder.create_template_dataset')
    def test_create_ds_template_no_context_no_var(self, mock_create_template_dataset):

        dim_sizes_dict = {"n_w": 271, "n_s": 10}

        variables_dict_defs = {"def2": "vars2"}
        metadata_defs = {"def1": "meta1", "def2": "meta1"}

        hdsb = HypernetsDSBuilder(variables_dict_defs=variables_dict_defs, metadata_defs=metadata_defs)
        self.assertRaises(NameError, hdsb.create_ds_template,
                          dim_sizes_dict=dim_sizes_dict,
                          ds_format="def1",
                          propagate_ds=None)

    @patch('hypernets_processor.data_io.hypernets_ds_builder.create_template_dataset')
    def test_create_ds_template_no_context_no_meta(self, mock_create_template_dataset):

        dim_sizes_dict = {"n_w": 271, "n_s": 10}

        variables_dict_defs = {"def1": "vars1", "def2": "vars2"}
        metadata_defs = {"def2": "meta1"}

        hdsb = HypernetsDSBuilder(variables_dict_defs=variables_dict_defs, metadata_defs=metadata_defs)
        self.assertRaises(RuntimeWarning, hdsb.create_ds_template,
                          dim_sizes_dict=dim_sizes_dict,
                          ds_format="def1",
                          propagate_ds=None)

    @patch('hypernets_processor.data_io.hypernets_ds_builder.create_template_dataset')
    def test_create_ds_template_runs_with_default_defs(self, mock_create_template_dataset):
        dim_sizes_dict = {"n_w": 271, "n_s": 10}

        hdsb = HypernetsDSBuilder()
        ds = hdsb.create_ds_template(dim_sizes_dict, "L_L2A")

        # test calls to create_template_dataset
        mock_create_template_dataset.assert_called()

    def test_return_ds_formats(self):

        variables_dict_defs = {"def1": "vars1", "def2": "vars2"}
        metadata_defs = {"def2": "meta1"}

        hdsb = HypernetsDSBuilder(variables_dict_defs=variables_dict_defs, metadata_defs=metadata_defs)
        ds_formats = hdsb.return_ds_formats()

        self.assertCountEqual(ds_formats, ["def1", "def2"])

    def test_return_ds_format_variable_names(self):

        variables_dict_defs = {"def1": {"var1": {"dim": ["dim1", "dim2"]},
                                        "var2": {"dim": ["dim2", "dim3", "dim4"]}},
                               "def2": {"var3": {"dim": ["dim10"]},
                                        "var4": {"dim": ["dim12"]}}}
        metadata_defs = {"def2": "meta1"}

        hdsb = HypernetsDSBuilder(variables_dict_defs=variables_dict_defs, metadata_defs=metadata_defs)
        ds_format_vars = hdsb.return_ds_format_variable_names("def1")

        self.assertCountEqual(ds_format_vars, ["var1", "var2"])

    def test_return_ds_format_dim_names(self):

        variables_dict_defs = {"def1": {"var1": {"dim": ["dim1", "dim2"]},
                                        "var2": {"dim": ["dim2", "dim3", "dim4"]}},
                               "def2": {"var3": {"dim": ["dim10"]},
                                        "var4": {"dim": ["dim12"]}}}
        metadata_defs = {"def2": "meta1"}

        hdsb = HypernetsDSBuilder(variables_dict_defs=variables_dict_defs, metadata_defs=metadata_defs)
        ds_format_dims = hdsb.return_ds_format_dim_names("def1")

        self.assertCountEqual(ds_format_dims, ["dim1", "dim2", "dim3", "dim4"])

    def test_create_empty_dim_sizes_dict(self):

        variables_dict_defs = {"def1": {"var1": {"dim": ["dim1", "dim2"]},
                                        "var2": {"dim": ["dim2", "dim3", "dim4"]}},
                               "def2": {"var3": {"dim": ["dim10"]},
                                        "var4": {"dim": ["dim12"]}}}
        metadata_defs = {"def2": "meta1"}

        hdsb = HypernetsDSBuilder(variables_dict_defs=variables_dict_defs, metadata_defs=metadata_defs)
        dim_sizes_dict = hdsb.create_empty_dim_sizes_dict("def1")

        expect_dim_sizes_dict = {"dim1": None, "dim2": None, "dim3": None, "dim4": None}

        self.assertDictEqual(dim_sizes_dict, expect_dim_sizes_dict)


if __name__ == '__main__':
    unittest.main()
