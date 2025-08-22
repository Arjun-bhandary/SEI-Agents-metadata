from google import genai
import pandas as pd
import re,json,os
from dotenv import load_dotenv
load_dotenv()
gemini_api = os.getenv("GEMINI_API_KEY")

class formula:
  def __init__(self):
    self.client = genai.Client(api_key=gemini_api)
  
  def extract_metadata(self, user_info: str, image_path: str):
    my_file = self.client.files.upload(file=image_path)

    prompt = f"""Given the image and the description of the information in the image, 
    your job is to make a metadata of the information and return it in JSON format. 
    Make sure to include information like the field of study, application, and what it is about.
    
    description: {user_info}
    """

    response = self.client.models.generate_content(
      model="gemini-2.5-flash",
      contents=[my_file, prompt],
    )
    text = response.candidates[0].content.parts[0].text
    cleaned_str = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()
        
    return json.loads(cleaned_str)
  
  def extract_summary(self, user_info: str, image_path: str):
    my_file = self.client.files.upload(file=image_path)

    prompt = f"""Given the image and the description of the information in the image, 
    your job is to make a SUMMARY of the information and return it in JSON format. 
    Inlcude everything important such that just by reading the JSON i can understand information about the paper.
    
    description: {user_info}
    """

    response = self.client.models.generate_content(
      model="gemini-2.5-flash",
      contents=[my_file, prompt],
    )
    text = response.candidates[0].content.parts[0].text
    cleaned_str = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()
        
    return json.loads(cleaned_str)
  

    