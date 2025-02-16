import snakeviz
from snakeviz.main import handlers
from tornado.testing import AsyncHTTPTestCase
import tornado
import unittest
from pathlib import Path
import os
import re
from io import StringIO
import argparse
import sys

RESTR = r'(?<!] \+ ")/static/'
REPLACE_WITH = \
    'https://cdn.rawgit.com/jiffyclub/snakeviz/v2.2.2/snakeviz/static/'
    
settings = {
    'static_path':  REPLACE_WITH, 
    'template_path': os.path.join(os.path.dirname(snakeviz.main.__file__), 'templates'),
    'debug': True,
    'gzip': True
}
app = tornado.web.Application(handlers, **settings)

def build_parser():
    parser = argparse.ArgumentParser(
        description='Start SnakeViz to view a Python profile.')

    parser.add_argument('filename', help='Python profile to view')
    return parser

class TestMyEndpoint(AsyncHTTPTestCase):
    file = ''
    output_file = ''
    def get_app(self):
        # Return the Tornado application to test
        return app

    def test_get_request(self):
        # Make a GET request to the endpoint
        response = self.fetch(f"/snakeviz/{self.file}")
        body = response.body.decode()
        body = re.sub(RESTR, REPLACE_WITH, body)
        with open(self.output_file, 'w') as f:
            f.write(body)
            
def cProfile2SnakeVizHtml(filename, output_filename=None, verbose=False):
    filename =  Path(filename).absolute()
    if output_filename is None:
        output_filename = f"{filename.stem}.html"
    TestMyEndpoint.file = filename
    TestMyEndpoint.output_file = output_filename
    
    if not verbose:
        stream = StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=0)
    unittest.main(defaultTest="TestMyEndpoint.test_get_request",
                  exit=False, **(dict(testRunner=runner) if not verbose else {}))
    
def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    p = args.filename
    sys.argv = [sys.argv[0]] # needed since otherwise unittest thinks the args are for itself
    cProfile2SnakeVizHtml(p, verbose=False)

if __name__ == '__main__':
    sys.exit(main())