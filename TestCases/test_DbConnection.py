import unittest
import pandas as pd
from unittest import mock

from unittest.mock import MagicMock, Mock, patch

import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from FastAPI.DbConnection import DbConnection

class TestSkillExtractorDetails(unittest.TestCase):
    
    #@patch('FastAPI.DbConnection.DbConnection.GetDbConnection')
    #def test_GetSkillId_with_cursor_rowcount_1(self, mock_GetDbConnection):
    def test_GetSkillId_with_cursor_rowcount_1(self):
        db_params = {
        'host': 'localhost',
        'database': 'BestResumeFitDB',
        'user': 'ashish',
        'password': 'fakepassword',
        }
        #mock_GetDbConnection.return_value = db_params
        
        result = DbConnection.GetDbConnection()
        self.assertIsNotNone(result)
        self.assertEqual(result['database'], 'OpenAI')
    
if __name__=='__main__':
    unittest.main()