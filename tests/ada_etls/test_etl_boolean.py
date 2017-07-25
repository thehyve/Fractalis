"""This module provides tests for the boolean ETL for Ada."""

import json

import pytest
import responses

from fractalis.data.etls.ada.etl_boolean import BooleanETL


# noinspection PyMissingOrEmptyDocstring,PyMissingTypeHints
class TestBooleanETL:

    etl = BooleanETL()

    valid_descriptor = {
        'dictionary': {
            'name': 'foo',
            'projection': 'foo',
            'label': 'bar',
            'fieldType': 'Boolean',
            'isArray': False
        },
        'data_set': 'baz'
    }

    def test_correct_handler(self):
        assert self.etl.can_handle(handler='ada', descriptor={
            'dictionary': {'fieldType': 'Boolean', 'isArray': False}
        })
        assert not self.etl.can_handle(handler='ada', descriptor={
            'dictionary': {'fieldType': 'Boolean', 'isArray': True}
        })
        assert not self.etl.can_handle(handler='transmart', descriptor={
            'dictionary': {'fieldType': 'Boolean', 'isArray': False}
        })
        assert not self.etl.can_handle(handler='ada', descriptor={
            'dictionary': {'fieldType': 'foo', 'isArray': False}
        })

    def test_extract_raises_readable_if_not_200(self):
        with responses.RequestsMock() as response:
            response.add(response.GET,
                         'http://foo.bar/studies/records/findCustom',
                         body='{}',
                         status=400,
                         content_type='application/json')
            with pytest.raises(ValueError) as e:
                self.etl.extract(server='http://foo.bar',
                                 token='',
                                 descriptor=self.valid_descriptor)
                assert '[400]' in e

    def test_extract_raises_readable_if_not_json(self):
        with responses.RequestsMock() as response:
            response.add(response.GET,
                         'http://foo.bar/studies/records/findCustom',
                         body='abc{//}',
                         status=200,
                         content_type='application/json')
            with pytest.raises(TypeError) as e:
                self.etl.extract(server='http://foo.bar',
                                 token='',
                                 descriptor=self.valid_descriptor)
                assert 'unexpected data' in e

    def test_returns_data_for_correct_input(self):
        body = json.dumps([{'a': True, '_id': {'$oid': '12345'}}])
        with responses.RequestsMock() as response:
            response.add(response.GET,
                         'http://foo.bar/studies/records/findCustom',
                         body=body,
                         status=200,
                         content_type='application/json')
            raw_data = self.etl.extract(server='http://foo.bar',
                                        token='',
                                        descriptor=self.valid_descriptor)
            assert isinstance(raw_data, list)

    def test_returns_df_for_correct_data(self):
        body = json.dumps([{'a': True, '_id': {'$oid': '12345'}}])
        with responses.RequestsMock() as response:
            response.add(response.GET,
                         'http://foo.bar/studies/records/findCustom',
                         body=body,
                         status=200,
                         content_type='application/json')
            raw_data = self.etl.extract(server='http://foo.bar',
                                        token='',
                                        descriptor=self.valid_descriptor)
            df = self.etl.transform(raw_data=raw_data,
                                    descriptor=self.valid_descriptor)
            assert df.shape == (1, 2)
            assert df.values.tolist() == [[True, '12345']]
            assert list(df) == ['a', 'id']
