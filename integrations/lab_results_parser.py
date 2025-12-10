"""Parser for lab results (blood tests, etc.)."""
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime
import re


class LabResultsParser:
    """Parses lab results from various formats."""
    
    @staticmethod
    def parse_json_results(file_path: str) -> Dict:
        """Parse lab results from JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def parse_text_results(text: str) -> Dict:
        """
        Parse lab results from plain text using simple heuristics.
        In production, you'd use more sophisticated NLP or structured formats.
        """
        # This is a basic parser - can be enhanced with NLP
        lines = text.split('\n')
        results = {
            "test_name": "",
            "test_date": "",
            "values": {},
            "reference_ranges": {},
            "flags": []  # High, Low, Normal
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to extract test name
            if "test" in line.lower() or "panel" in line.lower():
                results["test_name"] = line
            
            # Try to extract date
            if any(keyword in line.lower() for keyword in ["date", "collected", "drawn"]):
                results["test_date"] = line
            
            # Try to extract values (basic pattern matching)
            # Format: "Test Name: Value [Reference Range]"
            if ":" in line and any(char.isdigit() for char in line):
                parts = line.split(":")
                if len(parts) == 2:
                    test_name = parts[0].strip()
                    value_part = parts[1].strip()
                    
                    # Extract numeric value
                    numbers = re.findall(r'\d+\.?\d*', value_part)
                    if numbers:
                        results["values"][test_name] = float(numbers[0])
        
        return results
    
    @staticmethod
    def parse_pdf_results(file_path: str) -> Dict:
        """
        Parse lab results from PDF.
        This is a placeholder - in production, use PyPDF2 or pdfplumber.
        """
        # TODO: Implement PDF parsing
        raise NotImplementedError("PDF parsing not yet implemented")
    
    @staticmethod
    def normalize_results(results: Dict) -> Dict:
        """Normalize lab results to standard format."""
        normalized = {
            "test_type": "blood_test",  # Can be expanded
            "test_name": results.get("test_name", "Unknown"),
            "test_date": results.get("test_date", datetime.now().isoformat()),
            "results": results.get("values", {}),
            "reference_ranges": results.get("reference_ranges", {}),
            "flags": results.get("flags", []),
            "interpretation": ""
        }
        return normalized

