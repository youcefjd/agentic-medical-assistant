#!/usr/bin/env python3
"""Create simulated lab test results and MRI DICOM files for testing."""
import json
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
from datetime import datetime, date
from pathlib import Path
import numpy as np

# Create output directory
output_dir = Path("data/tests")
output_dir.mkdir(parents=True, exist_ok=True)

print("🔬 Creating test medical files...\n")

# 1. Create Blood Test Results (JSON format)
print("1️⃣ Creating blood test results...")
blood_test = {
    "test_name": "Complete Blood Count (CBC) and Metabolic Panel",
    "test_date": datetime.now().strftime("%Y-%m-%d"),
    "patient_id": "001",
    "patient_name": "Youcef Djeddar",
    "values": {
        "White Blood Cell Count (WBC)": 7.2,
        "Red Blood Cell Count (RBC)": 4.8,
        "Hemoglobin (HGB)": 14.5,
        "Hematocrit (HCT)": 42.3,
        "Platelet Count": 250,
        "Glucose": 95,
        "Creatinine": 0.9,
        "Blood Urea Nitrogen (BUN)": 12,
        "Sodium": 140,
        "Potassium": 4.2,
        "Chloride": 102,
        "Total Cholesterol": 185,
        "HDL Cholesterol": 55,
        "LDL Cholesterol": 115,
        "Triglycerides": 120
    },
    "reference_ranges": {
        "White Blood Cell Count (WBC)": {"min": 4.0, "max": 11.0, "unit": "10^3/μL"},
        "Red Blood Cell Count (RBC)": {"min": 4.5, "max": 5.5, "unit": "10^6/μL"},
        "Hemoglobin (HGB)": {"min": 13.5, "max": 17.5, "unit": "g/dL"},
        "Hematocrit (HCT)": {"min": 40.0, "max": 50.0, "unit": "%"},
        "Platelet Count": {"min": 150, "max": 450, "unit": "10^3/μL"},
        "Glucose": {"min": 70, "max": 100, "unit": "mg/dL"},
        "Creatinine": {"min": 0.7, "max": 1.3, "unit": "mg/dL"},
        "Blood Urea Nitrogen (BUN)": {"min": 7, "max": 20, "unit": "mg/dL"},
        "Sodium": {"min": 136, "max": 145, "unit": "mEq/L"},
        "Potassium": {"min": 3.5, "max": 5.0, "unit": "mEq/L"},
        "Chloride": {"min": 98, "max": 107, "unit": "mEq/L"},
        "Total Cholesterol": {"min": 0, "max": 200, "unit": "mg/dL"},
        "HDL Cholesterol": {"min": 40, "max": 999, "unit": "mg/dL"},
        "LDL Cholesterol": {"min": 0, "max": 100, "unit": "mg/dL"},
        "Triglycerides": {"min": 0, "max": 150, "unit": "mg/dL"}
    },
    "flags": [],
    "interpretation": "All values within normal ranges. No abnormalities detected."
}

blood_test_file = output_dir / "blood_test_001.json"
with open(blood_test_file, 'w') as f:
    json.dump(blood_test, f, indent=2)
print(f"   ✅ Created: {blood_test_file}")

# 2. Create Lipid Panel (JSON format)
print("\n2️⃣ Creating lipid panel results...")
lipid_panel = {
    "test_name": "Lipid Panel",
    "test_date": datetime.now().strftime("%Y-%m-%d"),
    "patient_id": "001",
    "patient_name": "Youcef Djeddar",
    "values": {
        "Total Cholesterol": 195,
        "HDL Cholesterol": 52,
        "LDL Cholesterol": 125,
        "Triglycerides": 135,
        "Cholesterol/HDL Ratio": 3.75
    },
    "reference_ranges": {
        "Total Cholesterol": {"min": 0, "max": 200, "unit": "mg/dL"},
        "HDL Cholesterol": {"min": 40, "max": 999, "unit": "mg/dL"},
        "LDL Cholesterol": {"min": 0, "max": 100, "unit": "mg/dL"},
        "Triglycerides": {"min": 0, "max": 150, "unit": "mg/dL"},
        "Cholesterol/HDL Ratio": {"min": 0, "max": 5.0, "unit": ""}
    },
    "flags": ["LDL slightly elevated"],
    "interpretation": "LDL cholesterol slightly above optimal range. Recommend dietary modifications and follow-up in 3 months."
}

lipid_panel_file = output_dir / "lipid_panel_001.json"
with open(lipid_panel_file, 'w') as f:
    json.dump(lipid_panel, f, indent=2)
print(f"   ✅ Created: {lipid_panel_file}")

# 3. Create Blood Test (Text format)
print("\n3️⃣ Creating blood test (text format)...")
blood_test_text = """LABORATORY RESULTS REPORT
Patient: Youcef Djeddar
Patient ID: 001
Date Collected: 2025-12-10
Date Reported: 2025-12-10

COMPLETE METABOLIC PANEL
------------------------
Glucose: 98 mg/dL [Reference: 70-100]
Creatinine: 0.95 mg/dL [Reference: 0.7-1.3]
BUN: 14 mg/dL [Reference: 7-20]
Sodium: 142 mEq/L [Reference: 136-145]
Potassium: 4.3 mEq/L [Reference: 3.5-5.0]
Chloride: 104 mEq/L [Reference: 98-107]
CO2: 24 mEq/L [Reference: 22-28]
Calcium: 9.8 mg/dL [Reference: 8.5-10.5]
Total Protein: 7.2 g/dL [Reference: 6.0-8.3]
Albumin: 4.5 g/dL [Reference: 3.5-5.0]
Bilirubin Total: 0.8 mg/dL [Reference: 0.2-1.2]
ALT: 28 U/L [Reference: 7-56]
AST: 25 U/L [Reference: 10-40]

All values within normal limits.
"""

blood_test_text_file = output_dir / "blood_test_text_001.txt"
with open(blood_test_text_file, 'w') as f:
    f.write(blood_test_text)
print(f"   ✅ Created: {blood_test_text_file}")

# 4. Create MRI DICOM file
print("\n4️⃣ Creating MRI DICOM file...")
try:
    # Create a minimal DICOM dataset
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.4'  # MR Image Storage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = '1.2.840.10008.1.2'  # Implicit VR Little Endian
    
    ds = FileDataset('test_mri.dcm', {}, file_meta=file_meta, preamble=b'\x00' * 128)
    
    # Patient information
    ds.PatientName = "Djeddar^Youcef"
    ds.PatientID = "001"
    ds.PatientBirthDate = "19800115"
    ds.PatientSex = "M"
    
    # Study information
    ds.StudyDate = datetime.now().strftime("%Y%m%d")
    ds.StudyTime = datetime.now().strftime("%H%M%S")
    ds.StudyInstanceUID = generate_uid()
    ds.StudyID = "ST001"
    ds.StudyDescription = "MRI Brain - Headache Evaluation"
    
    # Series information
    ds.SeriesInstanceUID = generate_uid()
    ds.SeriesNumber = 1
    ds.SeriesDescription = "T2 FLAIR Axial"
    ds.Modality = "MR"
    
    # Image information
    ds.InstanceNumber = 1
    ds.SOPInstanceUID = generate_uid()
    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.4'
    
    # Equipment information
    ds.Manufacturer = "Siemens"
    ds.ManufacturerModelName = "MAGNETOM Skyra"
    ds.InstitutionName = "Test Medical Center"
    ds.ReferringPhysicianName = "Dr. Smith"
    
    # Image characteristics
    ds.Rows = 256
    ds.Columns = 256
    ds.BitsAllocated = 16
    ds.BitsStored = 12
    ds.HighBit = 11
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    
    # Create a simple test image (simulated brain MRI pattern)
    pixel_array = np.random.randint(0, 4096, size=(256, 256), dtype=np.uint16)
    # Add some structure to make it look more realistic
    center_x, center_y = 128, 128
    y, x = np.ogrid[:256, :256]
    mask = (x - center_x)**2 + (y - center_y)**2 < 100**2
    pixel_array[mask] = pixel_array[mask] // 2  # Darker center (simulating brain)
    
    ds.PixelData = pixel_array.tobytes()
    
    # Save DICOM file
    mri_file = output_dir / "mri_brain_001.dcm"
    ds.save_as(str(mri_file), write_like_original=False)
    print(f"   ✅ Created: {mri_file}")
    print(f"      Size: {mri_file.stat().st_size / 1024:.2f} KB")
    
except Exception as e:
    print(f"   ⚠️  Error creating DICOM: {e}")
    print("   Creating a minimal DICOM file instead...")
    # Create a very basic DICOM file
    ds = Dataset()
    ds.PatientName = "Djeddar^Youcef"
    ds.PatientID = "001"
    ds.StudyDate = datetime.now().strftime("%Y%m%d")
    ds.Modality = "MR"
    ds.StudyDescription = "MRI Brain"
    mri_file = output_dir / "mri_brain_001.dcm"
    ds.save_as(str(mri_file))
    print(f"   ✅ Created minimal DICOM: {mri_file}")

# 5. Create CT Scan DICOM file
print("\n5️⃣ Creating CT Scan DICOM file...")
try:
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  # CT Image Storage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = '1.2.840.10008.1.2'
    
    ds = FileDataset('test_ct.dcm', {}, file_meta=file_meta, preamble=b'\x00' * 128)
    
    ds.PatientName = "Djeddar^Youcef"
    ds.PatientID = "001"
    ds.PatientBirthDate = "19800115"
    ds.PatientSex = "M"
    
    ds.StudyDate = datetime.now().strftime("%Y%m%d")
    ds.StudyTime = datetime.now().strftime("%H%M%S")
    ds.StudyInstanceUID = generate_uid()
    ds.StudyID = "ST002"
    ds.StudyDescription = "CT Chest - Routine Screening"
    
    ds.SeriesInstanceUID = generate_uid()
    ds.SeriesNumber = 1
    ds.SeriesDescription = "Chest Axial"
    ds.Modality = "CT"
    
    ds.InstanceNumber = 1
    ds.SOPInstanceUID = generate_uid()
    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
    
    ds.Manufacturer = "GE Healthcare"
    ds.ManufacturerModelName = "Revolution CT"
    ds.InstitutionName = "Test Medical Center"
    ds.ReferringPhysicianName = "Dr. Smith"
    
    ds.Rows = 512
    ds.Columns = 512
    ds.BitsAllocated = 16
    ds.BitsStored = 12
    ds.HighBit = 11
    ds.PixelRepresentation = 0
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    
    # Create test CT image
    pixel_array = np.random.randint(0, 4096, size=(512, 512), dtype=np.uint16)
    ds.PixelData = pixel_array.tobytes()
    
    ct_file = output_dir / "ct_chest_001.dcm"
    ds.save_as(str(ct_file), write_like_original=False)
    print(f"   ✅ Created: {ct_file}")
    print(f"      Size: {ct_file.stat().st_size / 1024:.2f} KB")
    
except Exception as e:
    print(f"   ⚠️  Error creating CT DICOM: {e}")

print("\n" + "="*60)
print("✅ ALL TEST FILES CREATED!")
print("="*60)
print("\nFiles created in: data/tests/")
print("\nYou can now upload these files in the Streamlit app:")
print("  - Blood Test (JSON): blood_test_001.json")
print("  - Lipid Panel (JSON): lipid_panel_001.json")
print("  - Blood Test (Text): blood_test_text_001.txt")
print("  - MRI Brain: mri_brain_001.dcm")
print("  - CT Chest: ct_chest_001.dcm")

