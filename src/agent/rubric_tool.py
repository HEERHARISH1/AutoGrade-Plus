import re
import csv
from typing import Dict, List, Optional
import pypdf

class RubricParser:
    """
    Parses grading rubrics from text or PDF into a structured format 
    that the ReAct agent can use as a tool.
    """
    
    def __init__(self):
        self.rubric_structure = {}

    def parse_text(self, text: str) -> Dict:
        """
        Parses a text-based rubric. 
        Expected format: "Criteria: [Name] - [Max Points] points - [Description]"
        """
        lines = text.split('\n')
        criteria = {}
        current_criterion = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Simple regex to find criteria patterns
            # Example: "1. Grammar (5 points): Check for spelling errors."
            match = re.search(r'(.+?)\s*\((\d+)\s*points?\):?\s*(.*)', line, re.IGNORECASE)
            
            if match:
                name = match.group(1).strip()
                points = int(match.group(2))
                desc = match.group(3).strip()
                
                criteria[name] = {
                    "max_points": points,
                    "description": desc
                }
            else:
                # If it's a continuation of the description
                if current_criterion:
                    # Append to previous description
                    pass 
                    
        self.rubric_structure = criteria
        return criteria

    def parse_pdf(self, pdf_path: str) -> Dict:
        """Extracts text from PDF and then parses it."""
        try:
            reader = pypdf.PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return self.parse_text(text)
        except Exception as e:
            return {"error": str(e)}

    def parse_csv(self, csv_path: str) -> Dict:
        """
        Parses a CSV rubric file.
        Expected columns: Criteria, Points, Description
        """
        try:
            criteria = {}
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get('Criteria', row.get('criteria', '')).strip()
                    points = int(row.get('Points', row.get('points', 0)))
                    desc = row.get('Description', row.get('description', '')).strip()
                    
                    if name:
                        criteria[name] = {
                            "max_points": points,
                            "description": desc
                        }
            
            self.rubric_structure = criteria
            return criteria
        except Exception as e:
            return {"error": str(e)}

    def parse_file(self, file_path: str) -> Dict:
        """
        Unified file parser. Detects file type and calls appropriate parser.
        Supports: .txt, .pdf, .csv
        """
        if file_path.endswith('.pdf'):
            return self.parse_pdf(file_path)
        elif file_path.endswith('.csv'):
            return self.parse_csv(file_path)
        else:
            # Assume text file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return self.parse_text(f.read())
            except Exception as e:
                return {"error": str(e)}

    def get_criteria_tool_desc(self) -> str:
        """Returns a string description of the rubric for the LLM tool definition."""
        desc = "Use this tool to check grading criteria. Available criteria:\n"
        for name, details in self.rubric_structure.items():
            desc += f"- {name}: {details['max_points']} points. {details['description']}\n"
        return desc

    def lookup_criteria(self, criteria_name: str) -> str:
        """
        Tool function: Returns details for a specific criteria.
        """
        # Fuzzy match or direct lookup
        for name, details in self.rubric_structure.items():
            if criteria_name.lower() in name.lower():
                return f"Criteria: {name}\nMax Points: {details['max_points']}\nDescription: {details['description']}"
        
        return "Criteria not found. Please check the available criteria list."
