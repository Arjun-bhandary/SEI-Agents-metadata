from google import genai
import pandas as pd
import re,json,os
from dotenv import load_dotenv
load_dotenv()
gemini_api = os.getenv("GEMINI_API_KEY")

class Dataset:
    """
    A class to handle dataset operations like metadata extraction, 
    metadata generation, and summarization using a generative AI model.
    """
    def __init__(self):
        pass

    @staticmethod
    def extract_column_metadata(csv_path: str) -> str:
        """
        Reads a CSV file and extracts metadata about its columns.

        Args:
            csv_path (str): The file path to the CSV.

        Returns:
            str: A formatted string describing each column's name and inferred type.
        """
        df = pd.read_csv(csv_path)

        def classify_dtype(series):
            if pd.api.types.is_datetime64_any_dtype(series):
                return "datetime"
            elif pd.api.types.is_numeric_dtype(series):
                return "numeric"
            elif pd.api.types.is_categorical_dtype(series):
                return "categorical"
            else:
                return "string"

        lines = []
        for col in df.columns:
            dtype = classify_dtype(df[col])
            lines.append(f"Column: {col} | Type: {dtype}")

        return "\n".join(lines)

    def generate_metadata(self, user_input: str, data_path: str,gemini_api: str) -> dict:
        """
        Generates structured metadata for a dataset in JSON format.

        Args:
            user_input (str): A natural language description of the dataset.
            data_path (str): The file path to the CSV data.

        Returns:
            dict: A dictionary containing the structured metadata.
        """
        column_data = self.extract_column_metadata(data_path)

        prompt = f"""
        You are a dataset metadata generator. 
        Given the dataset description and column details, generate complete metadata in a valid JSON format only.

        Requirements:
        - The JSON must include: title, description, columns (with name + type), source, license, update_frequency, and limitations.
        - Do not include any extra explanation or text outside of the JSON.

        dataset_information: "{user_input}"
        feature_information:
        {column_data}
        """
        client = genai.Client(api_key=gemini_api)
        resp = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        resp_text = resp.text
        cleaned_str = re.sub(r"^```json|```$", "", resp_text.strip(), flags=re.MULTILINE).strip()
        
        return json.loads(cleaned_str)

    def generate_summary(self, user_input: str, data_path: str,gemini_api: str) -> str:
        """
        Generates a natural language summary for a dataset.

        Args:
            user_input (str): A natural language description of the dataset.
            data_path (str): The file path to the CSV data.

        Returns:
            str: A text summary of the dataset.
        """
        column_data = self.extract_column_metadata(data_path)

        prompt = f"""
        You are a data science assistant. 
        Given the following description and column information for a dataset, please write a concise, easy-to-understand summary. 
        Describe what the dataset is about, what kind of information it contains, and what it might be used for.
        
        Make sure the output is in JSON format and it should include the concise summary, information like use cases, what is the field it can be used in, where and how the dataset was synthesised. 
        Dataset Description: "{user_input}"
        
        Column Information:
        {column_data}
        """
        client = genai.Client(api_key=gemini_api)
        resp = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        resp_text = resp.text
        cleaned_str = re.sub(r"^```json|```$", "", resp_text.strip(), flags=re.MULTILINE).strip()
        
        return json.loads(cleaned_str)
      
      