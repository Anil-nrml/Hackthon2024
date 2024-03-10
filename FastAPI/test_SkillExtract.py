import unittest
import pandas as pd
from unittest import mock

from unittest.mock import MagicMock, Mock, patch

from SkillExtract import SkillExtractorDetails

class TestSkillExtractorDetails(unittest.TestCase):

    # def test_GetSkillId(self):
    #     with mock.patch("psycopg2.connect") as psycopg2Connect_Mock:
    #         db_params = {'dbname': 'test_db', 'user': 'test_user', 'password': 'test_pass', 'host': 'localhost'}
    #         conn_Mock= psycopg2Connect_Mock.return_value
    #         cursor_Mock = conn_Mock.cursor.return_value
    #         #cursor_Mock.execute.return_value
    #         cursor_Mock.fetchone.return_value = [123456]
    #         jdmasterid = 912
    #         cursor_Mock.rowcount.return_value = 111
    #         commitMock = conn_Mock.commit.return_value

    #         result = SkillExtractorDetails.GetSkillId("Angular 16", jdmasterid, {});
    #         self.assertEqual(SkillExtractorDetails, 123456)
            
    @patch('SkillExtract.psycopg2.connect')
    def test_GetSkillId_with_cursor_rowcount_1(self, mock_connect):
        # Arrange
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        skill_name = "Python"
        jd_master_id = 912
        db_params = {'dbname': 'test_db', 'user': 'test_user', 'password': 'test_pass', 'host': 'localhost'}

        mock_cursor.fetchone.return_value = (1,) 
        mock_cursor.rowcount = 1 

        # Act
        skill_id = SkillExtractorDetails.GetSkillId(skill_name, jd_master_id, db_params)

        # Assert
        mock_connect.assert_called_once_with(**db_params)  
        self.assertEqual(mock_cursor.execute.call_count, 2)
        mock_cursor.execute.assert_any_call(
            "select skillid from skillmaster where upper(skilldetails) = (%s)", (skill_name.upper(),))
        mock_cursor.execute.assert_any_call(
            "SELECT skillid FROM jdSkilldetails WHERE skillid IN (%s) and jdMasterid in (%s)", (1, jd_master_id))
        self.assertEqual(skill_id, 1) 

    @patch('SkillExtract.psycopg2.connect')
    def test_GetSkillId_with_cursor_rowcount_0(self, mock_connect):
        #Arrange
        mock_cursor = MagicMock()
        mock_SQL = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor
        #mock_sql.return_value.SQL.return_value = mock_SQL

        skill_name = "Python"
        jd_master_id = 912
        db_params = {'dbname': 'test_db', 'user': 'test_user', 'password': 'test_pass', 'host': 'localhost'}

        mock_cursor.fetchone.return_value = (1,) 
        mock_cursor.rowcount = 0 

        # Act
        skill_id = SkillExtractorDetails.GetSkillId(skill_name, jd_master_id, db_params)

        # Assert
        mock_connect.assert_called_once_with(**db_params) 
        self.assertEqual(mock_cursor.execute.call_count, 3) 
        mock_cursor.execute.assert_any_call(
            "select skillid from skillmaster where upper(skilldetails) = (%s)", (skill_name.upper(),))
        mock_cursor.execute.assert_any_call(
            "SELECT skillid FROM jdSkilldetails WHERE skillid IN (%s) and jdMasterid in (%s)", (1, jd_master_id))
        self.assertEqual(skill_id, 1) 


    def test_skill_Validate_With_Python_Return_Success(self):
        data = {'skilldetails': ['PYTHON', 'Java', 'C++']}
        df = pd.DataFrame(data)
        self.assertEqual(SkillExtractorDetails.skill_Validate(df, 'Python'), 1)

    def test_skill_Validate_JavaScript_Return_Failure(self):
        data = {'skilldetails': ['PYTHON', 'JAVA', 'C++']}
        df = pd.DataFrame(data)
        self.assertEqual(SkillExtractorDetails.skill_Validate(df, 'JavaScript'), 0)

    def test_skill_Validate_With_Multi_Word_UpperCase_Return_Success(self):
        data = {'skilldetails': ['PYTHON', 'JAVA', 'A B C D']}
        df = pd.DataFrame(data)
        self.assertEqual(SkillExtractorDetails.skill_Validate(df, 'a b c d'), 1)

    def test_skill_Validate_With_DotNetCore_Return_Failure(self):
        data = {'skilldetails': ['PYTHON', 'JAVA', '.Net Core Web API']}
        df = pd.DataFrame(data)
        self.assertEqual(SkillExtractorDetails.skill_Validate(df, '.Net Core'), 0)

            
    @patch('SkillExtract.psycopg2.connect')
    @patch('SkillExtract.pd.read_sql_query')
    def test_getNewSkills(self, mock_read_sql_query, mock_connect):
        # Arrange
        mock_cursor = MagicMock()
        mock_conn = mock_connect.return_value
        mock_conn.cursor.return_value = mock_cursor

        mock_query_result = [('1', 'Python', 'Programming', 90),
                             ('2', 'Java', 'Programming', 85)]
        mock_read_sql_query.return_value = pd.DataFrame(mock_query_result, columns=['skillid', 'skilldetails', 'skilltype', 'skill_score'])

        mock_cursor.close.return_value = None
        mock_conn.close.return_value = None

        mock_db_params = {'database': 'your_db', 'user': 'your_user', 'password': 'your_password'}

        # Act
        result_df = SkillExtractorDetails.getNewSkills(mock_db_params)

        # Assertions
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertEqual(len(result_df), len(mock_query_result))

        self.assertTrue(all(result_df['skilldetails'].str.isupper()))

        mock_connect.assert_called_once_with(**mock_db_params)
        mock_conn.cursor.assert_called_once()
        mock_read_sql_query.assert_called_once_with("select skillid,skilldetails,skilltype,skill_score from skillmaster where weightage = -2", mock_conn)
        mock_read_sql_query.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('SkillExtract.SkillExtractorDetails.getNewSkills')
    @patch('SkillExtract.SkillExtractorDetails.skill_Validate')
    @patch('SkillExtract.SkillExtractorDetails.GetSkillId')
    def test_extractWords(self, mock_GetSkillId, mock_skill_Validate, mock_getNewSkills):
        # Mock the dependencies
        mock_getNewSkills.return_value = mock_df = MagicMock()
        mock_skill_Validate.return_value = True  # Mock skill validation to always return True

        # Define mock parameters
        mock_job_description = "This is a test job description."
        mock_JdMasterid = 123
        mock_db_params = {'database': 'your_db', 'user': 'your_user', 'password': 'your_password'}

        # Call the function with mock parameters
        result = SkillExtractorDetails.extractWords(mock_job_description, mock_JdMasterid, mock_db_params)

        # Assertions
        self.assertEqual(result, ["This", "is", "a", "test", "job", "description."])
        mock_getNewSkills.assert_called_once_with(mock_db_params)
        
        # Check if skill_Validate and GetSkillId were called for each word in the job description
        expected_calls = [unittest.mock.call(mock_df, word.strip()) for word in result]
        mock_skill_Validate.assert_has_calls(expected_calls, any_order=True)


    @patch('SkillExtract.psycopg2.connect')
    @patch('SkillExtract.pd.read_sql_query')
    def test_skill_check(self, mock_read_sql_query, mock_connect):
        # Arrange
        mock_conn = mock_connect.return_value

        mock_db_params = {'database': 'your_db', 'user': 'your_user', 'password': 'your_password'}
        mock_db_query = "SELECT skillname FROM FakeTableOrMockTable"

        mock_df_data = {'skillname': ['Python', 'Java', 'SQL']}
        mock_df = pd.DataFrame(mock_df_data)

        mock_read_sql_query.return_value = mock_df

        # Act
        result = SkillExtractorDetails.skill_check(mock_db_query, mock_db_params)

        # Assert
        expected_result = 'Python, Java, SQL'
        self.assertEqual(result, expected_result)


    @patch('SkillExtract.SkillExtractorDetails.skill_check')
    def test_display_skills(self, mock_skill_check):
        # Arrange
        mock_id = 1
        mock_db_params = {'database': 'your_db', 'user': 'your_user', 'password': 'your_password'}

        mock_skill_check.side_effect = ['Python, Java', 'Communication, Teamwork', 'Creativity', 'Problem Solving']

        # Act
        result = SkillExtractorDetails.display_skills(mock_id, mock_db_params)

        # Assert
        expected_result = 'Python, Java@Communication, Teamwork@Creativity Problem Solving'
        self.assertEqual(result, expected_result)


if __name__=='__main__':
    unittest.main()