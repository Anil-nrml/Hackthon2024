from concurrent.futures import ThreadPoolExecutor
import io
import itertools
import time
import PyPDF2
from google.cloud import storage
import docx2txt
from pathlib import Path
#import fitz

path_to_private_key = 'GCP_Key.json'

class GCSBlobReader:
    

    def __init__(self) -> None:
        self.str_folder_name_on_gcs = 'RESUME/data/'

        # Create the directory locally
        #Path(self.str_folder_name_on_gcs).mkdir(parents=True, exist_ok=True)

    def connect_to_gcs(self, bucket_url):
        storage_client = storage.Client.from_service_account_json(json_credentials_path=path_to_private_key)
        bucket = storage_client.get_bucket(bucket_url)
        return bucket
    
    def list_blobs(self, bucket_url):
        bucket = self.connect_to_gcs(bucket_url)
        blobs = bucket.list_blobs(prefix=self.str_folder_name_on_gcs)
        return blobs
    
    def read_all_files_from_gcs(self, bucketUrl, fileLimit):
        blobs = self.list_blobs(bucketUrl)
        #print(blobs)
        blobs_slice = itertools.islice(blobs, fileLimit)
        with ThreadPoolExecutor(max_workers=8) as executor:  # max_workers as needed
            
            futures = {executor.submit(blob.download_as_string): blob for blob in blobs_slice}
            #futures = {executor.submit(blob.download_as_string): blob for blob in blobs}
            
            listOfContent = []
            for future in futures:
                blob = futures[future]
                filename = blob.name
                try:
                    content = future.result()
                    if (filename.endswith("docx") | filename.endswith("doc")):
                        textfromdoc = docx2txt.process(io.BytesIO(content)) #docx2txt.process(f'./{blob.name}')
                        fileContentObj = {
                            'name': filename.replace(self.str_folder_name_on_gcs,''),
                            'content': textfromdoc
                            }
                        listOfContent.append(fileContentObj)
                    
                    elif filename.endswith("pdf"):
                        text = ''
                        reserve_pdf_on_memory = io.BytesIO(content)
                        load_pdf = PyPDF2.PdfReader(reserve_pdf_on_memory)
                        for page in load_pdf.pages:
                            text += page.extract_text()
                        fileContentObj = {'name': filename.replace(self.str_folder_name_on_gcs,''),
                                    'content': text
                                    }
                        listOfContent.append(fileContentObj)
                        #file_contents.append((blob.name, content))
                        
                        # doc = fitz.open(stream = io.BytesIO(content), filetype="pdf") 
                        # for page in doc: 
                        #     text += page.get_text() 
                        # fileContentObj = {'name': filename.replace(self.str_folder_name_on_gcs,''),
                        #             'content': text
                        #             }
                        # listOfContent.append(fileContentObj)
                        # doc.close()
                
                except Exception as e:
                    print(f"Error reading {blob.name}: {e}")
                    
        return listOfContent 
    
if __name__ == '__main__':
    gcsReader = GCSBlobReader()
    starttime = time.time()
    listOfContent = gcsReader.read_all_files_from_gcs('hackathon1415',20)
    endtime = time.time()
    print(listOfContent[0]['name'])
    print(endtime - starttime)
    print(len(listOfContent))