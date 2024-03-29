import os
import sys

sys.path.append(os.path.abspath('.'))

import unittest
from unittest.mock import MagicMock, patch

from src.handler.driver_session import *
from src.my_util import identity


class ParameterTest(unittest.TestCase):
    def test_get_next_value(self):
        excepted = [0, 1, 2]
        param = SearchParameter(..., identity, identity)
        self.assertEqual(param.get_next_values(..., lambda x, y: [*range(3)]), excepted)
        
class ParameterPatternTest(unittest.TestCase):
    def setUp(self) -> None:
        self.session = DriverSession(MagicMock(), MagicMock())
        return super().setUp()
    
    def test_level_1(self):
        node = MagicMock()
        node.url = 'https://classroom.google.com/u/1/c/AAAAAAAAAAAAAAAA'
        node.key = 'test'
        node.tree_height = 1
        
        result = self.session.next_key_url(node)
        self.assertIsInstance(result, zip)
                
    def test_level_3(self):
        not_exist_node = MagicMock()
        not_exist_node.url = 'https://drive.google.com/file/d/AAAAAAAAAAAAAAAA/view?usp=drive_web&authuser=1'
        not_exist_node.key = 'test'
        not_exist_node.tree_height = 3
        
        self.assertListEqual(self.session.next_key_url(not_exist_node), [(None, None)])
        
        path = Path(__file__)
        exist_node = MagicMock()
        exist_node.url = 'https://drive.google.com/file/d/AAAAAAAAAAAAAAAA/view?usp=drive_web&authuser=1'
        exist_node.key = path.name
        exist_node.tree_height = 3
        exist_node.to_path.return_value = path.parent
        
        self.session.next_key_url(exist_node)
        
class DriverSessionTest(unittest.TestCase):
    def test_close(self):
        session = DriverSession()
        session.close()
        
if __name__ == '__main__':
    unittest.main()