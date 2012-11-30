import os
import unittest
import zipfile
import json
import nose
from StringIO import StringIO
from xdocreport_restclient import invoke_service, get_info

DOCUMENT_DIR = os.path.join(os.path.dirname(__file__), 'testdocuments')


class TestClient(unittest.TestCase):
    "One method will be attached for each odt file in testdocuments/"


def setUp(self):
    for filename in os.listdir(DOCUMENT_DIR):
        if filename.endswith('.out.odt'):
            os.unlink(os.path.join(DOCUMENT_DIR, filename))


def make_method(filename):
    def test_report(self):
        path = os.path.join(DOCUMENT_DIR, filename)
        datapath = os.path.join(DOCUMENT_DIR, filename + '.json')
        with open(datapath) as datapathfh:
            data = json.loads(datapathfh.read())
        with open(path) as fh:
            res = invoke_service(template=fh, data=data,
                                 data_type='JSON', template_engine='Velocity')
        ziparchive = zipfile.ZipFile(StringIO(res), "r")
        xmldata = ziparchive.read("content.xml")
        for string in get_string_values(data):
            self.assertTrue(str(string) in xmldata)
        outpath = os.path.join(DOCUMENT_DIR, filename.lower())
        outpath = outpath.replace('.odt', '.out.odt')
        with open(outpath, 'w') as fh:
            fh.write(res)

    test_report.__name__ = 'test_' + filename.replace('.', '_')
    return test_report

for filename in os.listdir(DOCUMENT_DIR):
    if filename.lower().endswith('.odt') and '.out.' not in filename:
        safe_filename = filename.replace('.', '_')
        setattr(TestClient, safe_filename, make_method(filename))


def get_string_values(dictionary):
    for key, value in dictionary.items():
        if isinstance(value, basestring):
            yield value
        elif isinstance(value, dict):
            for val in get_string_values(value):
                yield val


def test_get_string_values():
    res = sorted(list(get_string_values(
        {'a': 1, 'b': {'c': {'d': 'hereami'}, 'e': 'a'}}
    )))
    nose.tools.assert_equal(res, ['a', 'hereami'])


def test_get_info():
    data = {
     "project": {"name": "The big project"},
     "developers": [
      {
       "lastName": "Leclercq",
       "name": "Pascal"
      },
      {
       "lastName": "Zerr",
       "name": "Angelo"
      },
      {
       "lastName": "Tomatis",
       "name": "Silvio"
      }
     ]
    }
    res = tuple(get_info(data))
    res = sorted(res, key=lambda x: x.name)
    nose.tools.assert_equal(len(res), 3)
    nose.tools.assert_equal(res[0].name, 'developers.lastName')
    nose.tools.assert_equal(res[0].list, 'true')
    nose.tools.assert_equal(res[1].name, 'developers.name')
    nose.tools.assert_equal(res[1].list, 'true')
    nose.tools.assert_equal(res[2].name, 'project.name')
    nose.tools.assert_equal(res[2].list, 'false')
