import unittest
from unittest.mock import MagicMock, Mock, patch
from datetime import date
import pandas as pd

import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from FastAPI.UploadFile import UploadOpenFile  # Replace 'your_module' with the actual module name

class TestUploadOpenFile(unittest.TestCase):

    @patch('FastAPI.UploadFile.psycopg2.connect')
    @patch('FastAPI.UploadFile.pd.read_sql_query')
    @patch('FastAPI.UploadFile.sql.SQL')
    def test_uploadFile(self, mock_sql, mock_read_sql_query, mock_connect):
        # Arrange
        mock_text = "Sample job description"
        mock_file_path = "/path/to/your/file.txt"
        mock_db_params = {'database': 'your_db', 'user': 'your_user', 'password': 'your_password'}

        mock_connect.return_value.cursor.return_value.__enter__.return_value = MagicMock()
        mock_read_sql_query.return_value = pd.DataFrame({'max(jdmasterid)': [42]})
        mock_sql.return_value = "mocked_query"

        # Act
        result = UploadOpenFile.uploadFile(mock_text, mock_file_path, mock_db_params)

        # Assert
        self.assertEqual(result, 43)
        
    @patch('FastAPI.UploadFile.psycopg2.connect')
    @patch('FastAPI.UploadFile.pd.read_sql_query')
    @patch('FastAPI.UploadFile.sql.SQL')
    def test_uploadFile_With_Empty_Row(self, mock_sql, mock_read_sql_query, mock_connect):
        # Arrange
        mock_text = "Sample job description"
        mock_file_path = "/path/to/your/file.txt"
        mock_db_params = {'database': 'your_db', 'user': 'your_user', 'password': 'your_password'}

        mock_connect.return_value.cursor.return_value.__enter__.return_value = MagicMock()
        mock_read_sql_query.return_value = pd.DataFrame({'max(jdmasterid)': []})
        mock_sql.return_value = "mocked_query"

        # Act
        result = UploadOpenFile.uploadFile(mock_text, mock_file_path, mock_db_params)

        # Assert
        self.assertEqual(result, 1)

        

if __name__=='__main__':
    unittest.main()