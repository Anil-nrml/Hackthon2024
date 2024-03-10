import io 
import PyPDF2
import docx2txt 
class ExtractContentFromFile:
    def ExtractDataFromFile(FileName,file):
        text =''
        print(text)
        if FileName.endswith("pdf"):
            reserve_pdf_on_memory = io.BytesIO(file)
            load_pdf = PyPDF2.PdfReader(reserve_pdf_on_memory)
            for page in load_pdf.pages:
                text += page.extract_text()
        
        elif FileName.endswith("doc") or FileName.endswith("docx"):
            text = docx2txt.process(file)
            text = text.read()
        
        else:
            text = file.decode('utf-8')
        return text    