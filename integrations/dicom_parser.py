"""DICOM file parser for medical imaging."""
import pydicom
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class DICOMParser:
    """Parses DICOM files (MRIs, CT scans, X-rays, etc.)."""
    
    @staticmethod
    def parse_dicom_file(file_path: str) -> Dict:
        """
        Parse a DICOM file and extract metadata.
        
        Returns:
            Dictionary with DICOM metadata and information
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"DICOM file not found: {file_path}")
        
        try:
            ds = pydicom.dcmread(file_path)
            
            # Extract common DICOM tags
            result = {
                "patient_name": str(ds.get("PatientName", "")),
                "patient_id": str(ds.get("PatientID", "")),
                "patient_birth_date": str(ds.get("PatientBirthDate", "")),
                "study_date": str(ds.get("StudyDate", "")),
                "study_time": str(ds.get("StudyTime", "")),
                "modality": str(ds.get("Modality", "")),  # CT, MR, XR, etc.
                "study_description": str(ds.get("StudyDescription", "")),
                "series_description": str(ds.get("SeriesDescription", "")),
                "manufacturer": str(ds.get("Manufacturer", "")),
                "manufacturer_model": str(ds.get("ManufacturerModelName", "")),
                "institution_name": str(ds.get("InstitutionName", "")),
                "referring_physician": str(ds.get("ReferringPhysicianName", "")),
                "file_path": file_path,
                "file_size": Path(file_path).stat().st_size,
            }
            
            # Try to extract image dimensions if available
            if hasattr(ds, "Rows") and hasattr(ds, "Columns"):
                result["image_dimensions"] = {
                    "rows": ds.Rows,
                    "columns": ds.Columns
                }
            
            return result
        except Exception as e:
            raise ValueError(f"Error parsing DICOM file: {e}")
    
    @staticmethod
    def extract_image_from_dicom(file_path: str, output_path: str = None) -> Optional[str]:
        """
        Extract image from DICOM file and save as PNG.
        
        Returns:
            Path to extracted image
        """
        try:
            ds = pydicom.dcmread(file_path)
            
            if not hasattr(ds, "pixel_array"):
                return None
            
            from PIL import Image
            import numpy as np
            
            # Normalize pixel array
            pixel_array = ds.pixel_array
            normalized = ((pixel_array - pixel_array.min()) / 
                         (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)
            
            # Convert to PIL Image
            image = Image.fromarray(normalized)
            
            # Save
            if output_path is None:
                output_path = str(Path(file_path).with_suffix(".png"))
            
            image.save(output_path)
            return output_path
        except Exception as e:
            print(f"Error extracting image: {e}")
            return None

