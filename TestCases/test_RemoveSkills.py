import unittest
from unittest.mock import MagicMock, Mock, patch

import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from FastAPI.RemoveSkills import RemoveSkill  



class TestRemoveSkill(unittest.TestCase):

    @patch('FastAPI.RemoveSkills.psycopg2.connect')
    def test_RemoveSkillDetails(self, mock_connect):
        # Arrange
        mock_db_params = {'database': 'your_db', 'user': 'your_user', 'password': 'your_password'}
        mock_skill_name = "Python"

        mock_connect.return_value.cursor.return_value.__enter__.return_value = MagicMock()

        # Act
        RemoveSkill.RemoveSkillDetails(mock_db_params, mock_skill_name)

        # Assert
        mock_connect.assert_called_once_with(**mock_db_params)
        mock_connect.return_value.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()