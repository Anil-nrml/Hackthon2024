import io
import unittest
from unittest.mock import MagicMock, Mock, patch, call

import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from FastAPI.ExtractContentsFromFile import ExtractContentFromFile 

class TestExtractContentFromFile(unittest.TestCase):

    @patch('FastAPI.ExtractContentsFromFile.io.BytesIO')
    @patch('FastAPI.ExtractContentsFromFile.PyPDF2.PdfReader')
    @patch('FastAPI.ExtractContentsFromFile.docx2txt.process')
    def test_ExtractDataFromFile(self, mock_process, mock_PdfReader, mock_BytesIO):
        # Arrange
        mock_file_name_pdf = "sample.pdf"
        mock_file_name_docx = "sample.docx"
        mock_file_name_txt = "sample.txt"
        mock_pdf_file = b'Mock PDF Content'
        mock_docx_file = 'Mock DOCX Content'
        mock_txt_file = b'Mock Text Content'

        mock_PdfReader_instance = mock_PdfReader.return_value
        mock_PdfReader_instance.pages = [MagicMock(extract_text=MagicMock(return_value='PDF Page 1')),
                                         MagicMock(extract_text=MagicMock(return_value='PDF Page 2'))]

        mock_process.return_value = MagicMock(read=MagicMock(return_value='Mock DOCX Text'))

        # Act
        result_pdf = ExtractContentFromFile.ExtractDataFromFile(mock_file_name_pdf, mock_pdf_file)
        result_docx = ExtractContentFromFile.ExtractDataFromFile(mock_file_name_docx, mock_docx_file)
        result_txt = ExtractContentFromFile.ExtractDataFromFile(mock_file_name_txt, mock_txt_file)

        # Assertions
        self.assertEqual(result_pdf, 'PDF Page 1PDF Page 2')
        self.assertEqual(result_docx, 'Mock DOCX Text')
        self.assertEqual(result_txt, 'Mock Text Content')

if __name__ == '__main__':
    unittest.main()