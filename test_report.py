"""
Test script for report generator
"""

from Src.report_generator import MedicalReportGenerator
from PIL import Image
from datetime import datetime
import os

def test_report_generation():
    """Test the report generation functionality."""
    
    print("🧪 Testing Report Generator...")
    
    # Create a dummy MRI image
    dummy_image = Image.new('RGB', (224, 224), color='gray')
    
    # Sample data
    patient_info = {
        'name': 'John Doe',
        'patient_id': 'P-2024-001',
        'age': 65,
        'gender': 'Male',
        'date': datetime.now().strftime("%Y-%m-%d"),
        'notes': 'Test patient for report generation'
    }
    
    doctor_info = {
        'name': 'Dr. Jane Smith',
        'role': 'Neurologist'
    }
    
    prediction = "Mild Alzheimer's"
    
    probabilities = {
        "Mild Alzheimer's": 0.65,
        "Moderate Alzheimer's": 0.20,
        "Non-demented": 0.10,
        "Very Mild Alzheimer's": 0.05
    }
    
    try:
        # Generate report
        print("📄 Generating report...")
        report_gen = MedicalReportGenerator()
        pdf_buffer = report_gen.generate_report(
            patient_info=patient_info,
            prediction=prediction,
            probabilities=probabilities,
            mri_image=dummy_image,
            doctor_info=doctor_info
        )
        
        # Save to file
        output_file = "test_report.pdf"
        with open(output_file, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"✅ Report generated successfully!")
        print(f"📁 Saved to: {os.path.abspath(output_file)}")
        print(f"📊 File size: {len(pdf_buffer.getvalue())} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_report_generation()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Tests failed!")
