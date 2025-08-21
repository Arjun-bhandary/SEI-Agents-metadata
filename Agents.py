import requests
import xml.etree.ElementTree as ET
from google import genai
from dotenv import load_dotenv
import os
import re
import json
import pandas as pd

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

class Prompts:
  def __init__(self):
    pass

  def meta_data_prompt(self, metadata_xml, body_xml, references_xml):
    prompt = f"""
    You are a research paper parser. 
    Given the TEI XML segments extracted from GROBID, convert them into a structured JSON object with fields:
    - citation_key
    - authors (list of "First,Last")
    - title
    - date, year, month, day
    - doi
    - eprint (arXiv or other)
    - abstract
    - high level overview of the paper
    - specialities
    - distinguing features
    - publisher
    - keywords
    - bibtex string

    Metadata XML:
    {metadata_xml}
    Body XML:
    {body_xml}
    References XML:
    {references_xml}
    If a field is missing in the XML, leave it as an empty string.
    The final output should be JSON containing all fields above, and include a complete BibTeX entry.
    """
    return prompt

  def summary_prompt(self, metadata_xml, body_xml, references_xml):
    prompt = f"""
    You are a research paper parser. 
    Given the TEI XML segments extracted from GROBID, convert them into a structured JSON object with fields:
    - abstract
    - keywords
    - problem_statement
    - methodology_summary
    - results_summary
    - conclusion_summary
    - contributions
    - field_of_study
    - subfields
    - tasks
    - datasets_used(if any)
    - code_link(if any)
    - application_domains

    Metadata XML:
    {metadata_xml}

    Body XML:
    {body_xml}

    References XML:
    {references_xml}

    If a field is missing in the XML, leave it as an empty string.
    If there are a any other features to be added to the JSON do it.
    The final output should be JSON containing all fields above, and include a complete BibTeX entry.
    """
    return prompt

class Agent:
  def __init__(self, api_key):
    self.client = genai.Client(api_key=api_key)
    self.prompts = Prompts()

  def _call_model_and_parse_json(self, prompt, model="gemini-1.5-flash"):
    resp = self.client.models.generate_content(model=model, contents=prompt)
    resp_text = getattr(resp, "text", str(resp))
    cleaned_str = re.sub(r"^```json|```$", "", resp_text.strip(), flags=re.MULTILINE).strip()
    try:
      return json.loads(cleaned_str)
    except json.JSONDecodeError:
      first = cleaned_str.find("{")
      last = cleaned_str.rfind("}")
      if first != -1 and last != -1 and last > first:
        try:
          return json.loads(cleaned_str[first:last+1])
        except json.JSONDecodeError:
          pass
      raise ValueError("Could not parse JSON from model response:\n" + cleaned_str)

  def generate_meta_data(self, metadata_xml, body_xml, references_xml):
    prompt = self.prompts.meta_data_prompt(metadata_xml, body_xml, references_xml)
    return self._call_model_and_parse_json(prompt)

  def generate_summary(self, metadata_xml, body_xml, references_xml):
    prompt = self.prompts.summary_prompt(metadata_xml, body_xml, references_xml)
    return self._call_model_and_parse_json(prompt)

class Paper:
  def __init__(self, pdf_path, grobid_url="https://kermitt2-grobid.hf.space"):
    self.pdf_path = pdf_path
    self.grobid_url = grobid_url
    self.xml_meta_data = None
    self.head = ""
    self.body = ""
    self.tail = ""
    self._meta_data = None
    self._summary = None
    self._agent = Agent(api_key=gemini_api_key)

  def processFulltextDocument(self):
    with open(self.pdf_path, "rb") as f:
      files = {"input": f}
      params = {"consolidate": "1"}
      r = requests.post(f"{self.grobid_url}/api/processFulltextDocument", files=files, params=params, timeout=60)
      r.raise_for_status()
      self.xml_meta_data = r.text
      return self.xml_meta_data

  def parse_grobid_output(self):
    if not self.xml_meta_data:
      self.processFulltextDocument()
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    root = ET.fromstring(self.xml_meta_data)
    metadata_elem = root.find(".//tei:teiHeader", ns)
    body_elem = root.find(".//tei:body", ns)
    refs_elem = root.find(".//tei:listBibl", ns)
    self.head = ET.tostring(metadata_elem, encoding="unicode") if metadata_elem is not None else ""
    self.body = ET.tostring(body_elem, encoding="unicode") if body_elem is not None else ""
    self.tail = ET.tostring(refs_elem, encoding="unicode") if refs_elem is not None else ""
    return self.head, self.body, self.tail

  def get_meta_data(self):
    if self._meta_data is None:
      if not self.head and not self.body and not self.tail:
        self.parse_grobid_output()
      self._meta_data = self._agent.generate_meta_data(self.head, self.body, self.tail)
    return self._meta_data

  def get_summary(self):
    if self._summary is None:
      if not self.head and not self.body and not self.tail:
        self.parse_grobid_output()
      self._summary = self._agent.generate_summary(self.head, self.body, self.tail)
    return self._summary


    





    