import os
import sys

sys.path.append(os.path.abspath('.'))

import unittest
from pathlib import Path
from shutil import rmtree
from unittest.mock import MagicMock, patch

from src.data import *
from src.my_util import arrow
from src.my_io import *


class SettingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path('./for_test')
        self.path.mkdir(parents=True, exist_ok=True)
        return super().setUp()
    
    def tearDown(self) -> None:
        rmtree(self.path)
        return super().tearDown()
    
    def test_invailed_path(self):
        self.assertRaises(FileNotFoundError, save, Path('.'), SettingData())
        self.assertRaises(FileNotFoundError, save, self.path, SettingData())
        self.assertRaises(FileNotFoundError, load, Path('.'))
        
    def test_try_save(self):
        path = self.path.joinpath('setting.json')
        try_save(path, SettingData())
        self.assertTrue(path.exists())
        
        x = path.read_text()
        self.assertTrue(x) #空文字ではない
        
    def test_load(self):
        self.assertRaises(FileNotFoundError, load, Path('HogeHoge'))
        self.assertRaises(FileNotFoundError, load, Path('HogeHoge.json'))
        
        path = self.path.joinpath('setting.json')
        target = SettingData()
        try_save(path, target)
        
        result = load(path)
        self.assertIsInstance(result, target.__class__)
        
    def test_try_load(self):
        self.assertEqual(try_load(Path('NotExists')), SettingData())