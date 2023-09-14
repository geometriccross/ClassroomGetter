import os
import sys

sys.path.append(os.path.abspath('.'))

import tkinter as tk
import unittest
from unittest.mock import patch

from src.gui.custum_widgets import *


class TimeSettersTest(unittest.TestCase):
    def test_is_current_value(self):
        root = tk.Tk()
        setters = TimeSetters(root)
        routine = RoutineData(1,1,1,1)
        setters.set(routine)
        self.assertEqual(setters.values(), routine)
        
class TimerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = tk.Tk()
        
    @patch('src.gui.custum_widgets.info_boxes.node_box.NodeBox', spec=NodeBox)
    def test_update_clock(self, m_node_box):
        m_node_box.time = RoutineData(1/60)
        timer = Timer(self.root, m_node_box)
        timer.update_clock(m_node_box, 1)