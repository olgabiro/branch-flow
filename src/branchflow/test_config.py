from unittest import TestCase

from branchflow import add_project
from branchflow.cli import new
from branchflow.config import add_task


class Test(TestCase):
    def test_load_config(self):
        add_project("test2", "./branchflow")
        self.fail()