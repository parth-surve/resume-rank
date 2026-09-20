import requests
from pathlib import Path
import pymupdf
import io
url = "https://d8it4huxumps7.cloudfront.net/uploads/profileData/files/46468262/_698dc8b821567.pdf"
def download_resume_in_memory(url:str,timeout:int=15):
   #downloads resume into the RAM and extracts the text without creating any local file
   try:
       #step 1 : Download file bytes directly into RAM
       response = requests.get(url,timeout=timeout)
       if response.status_code == 200 :
           #Load raw PDF bytes straight into RAM 
           pdf_bytes = io.BytesIO(response.content)
           doc = pymupdf.open(stream = pdf_bytes,filetype = "pdf")
           if doc.is_encrypted:
               return {"success":False,"reason":"Encrypted PDF file"}
           textpages = [page.get_text("text") for page in doc if page.get_text("text").strip()]
           full_text ="\n".join(textpages).strip()
           if not full_text:
               return {"success": False,"resume_text":"","reason":"Scanned image or empty PDF"}
           return {"success":True,"resume_text":full_text,"reason":None}
       else:
           return {"success": False,"resume_text":"","reason":f"HTTP status {response.status_code}"}
   except requests.exceptions.Timeout:
       return{"success":False,"resume_text":"","reason":"Connection timeout"}
   except requests.exceptions.RequestException as e:
       return {"success": False,"resume_text":"","reason":f"Network failure:{type(e).__name__}"}
   except Exception as e:
       return {"success":False,"resume_text":"","reason":"Processing error: {str(e)}"}
print(download_resume_in_memory(url))
