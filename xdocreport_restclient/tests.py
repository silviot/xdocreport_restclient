import os
import unittest
import zipfile
import json
import nose
import collections
from StringIO import StringIO
from xdocreport_restclient import report, get_info

DOCUMENT_DIR = os.path.join(os.path.dirname(__file__), 'testdocuments')


class TestClient(unittest.TestCase):
    "One method will be attached for each odt file in testdocuments/"


def setUp(self):
    for filename in os.listdir(DOCUMENT_DIR):
        if filename.endswith('.out.odt'):
            os.unlink(os.path.join(DOCUMENT_DIR, filename))


def make_method(filename):
    def test_report(self):
        file_extension = filename.split('.')[-1]
        path = os.path.join(DOCUMENT_DIR, filename)
        datapath = os.path.join(DOCUMENT_DIR, filename + '.json')
        with open(datapath) as datapathfh:
            data = json.loads(datapathfh.read())
        with open(path) as fh:
            res = report(template=fh, data=data, document_type=file_extension,
                                 template_engine='Velocity')
        ziparchive = zipfile.ZipFile(StringIO(res), "r")
        if file_extension == 'odt':
            xmldata = ziparchive.read("content.xml")
        elif file_extension == 'docx':
            xmldata = ziparchive.read("word/document.xml")
        else:
            raise RuntimeError("%s is an unknown file" % filename)
        for string in get_string_values(data):
            self.assertTrue(str(string) in xmldata)
        lowerpath = os.path.join(DOCUMENT_DIR, filename.lower())
        outpath = '.'.join(lowerpath.split('.')[:-1] + ['out', file_extension])
        with open(outpath, 'w') as fh:
            fh.write(res)
        for output_type in ('pdf', 'xhtml'):
            # generate a PDF and an html (smoke testing)
            with open(path) as fh:
                res = report(template=fh, data=data, document_type=file_extension,
                                     template_engine='Velocity', output_type=output_type)
            outpath = '.'.join(lowerpath.split('.')[:-1] + ['out', output_type])
            with open(outpath, 'w') as fh:
                fh.write(res)


    test_report.__name__ = 'test_' + filename.replace('.', '_')
    return test_report

for filename in os.listdir(DOCUMENT_DIR):
    if not '.' in filename:
        continue
    file_extension = filename.split('.')[-1]
    if file_extension in ('odt', 'docx') and '.out.' not in filename:
        safe_filename = filename.replace('.', '_')
        setattr(TestClient, safe_filename, make_method(filename))


def get_string_values(dictionary):
    for key, value in dictionary.items():
        if isinstance(value, basestring):
            yield value
        elif isinstance(value, dict):
            for val in get_string_values(value):
                yield val
        elif isinstance(value, collections.Iterable):
            for outer in value:
                for el in get_string_values(outer):
                    yield el


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
