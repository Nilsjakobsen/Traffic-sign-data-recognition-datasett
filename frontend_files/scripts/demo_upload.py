"""
============================================
FRONTEND CODE - Demo/Test Helper
============================================
This script helps verify the Flask backend is working
by simulating what the React frontend does
"""

import requests
from pathlib import Path
import json

def demo_upload(pdf_path):
    """
    Demo function showing how to upload a PDF to the backend
    This mimics what the React frontend does
    """
    
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        return
    
    print(f"📄 Uploading: {pdf_path}")
    print("⏳ Processing... (this may take a while)")
    
    try:
        # Open and send the file
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            response = requests.post(
                'http://localhost:5000/api/upload',
                files=files,
                timeout=300  # 5 minute timeout
            )
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Success!")
            print(f"📊 {data['message']}")
            print(f"\nDetected {len(data['signs'])} signs:\n")
            
            for i, sign in enumerate(data['signs'], 1):
                print(f"{i}. {sign['predicted_class']} - "
                      f"{sign['confidence']*100:.2f}% confidence "
                      f"({sign['filename']})")
            
            # Show where images are
            if data['signs']:
                print(f"\n📸 Images available at:")
                print(f"   http://localhost:5000/api/sign-image/{data['session_id']}/signs/...")
            
            return data
        else:
            print(f"\n❌ Error {response.status_code}")
            print(response.json())
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to backend.")
        print("   Make sure Flask is running: python app.py")
        return None
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None

def main():
    print("=" * 60)
    print("Sign Recognition Backend - Demo Upload")
    print("=" * 60)
    print("\nThis script demonstrates how to use the Flask backend API")
    print("Make sure the backend is running: python app.py\n")
    
    # Check if backend is running
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running\n")
        else:
            print("⚠️  Backend returned unexpected status\n")
    except:
        print("❌ Backend is not running. Start it with: python app.py\n")
        return
    
    # Example: Upload the sample PDF if it exists
    sample_pdf = "APV_plan_GDPR_trygg/AP22222-gdpr fixed AF Gruppen.pdf"
    
    if Path(sample_pdf).exists():
        print(f"Found sample PDF: {sample_pdf}")
        print("Uploading...\n")
        result = demo_upload(sample_pdf)
        
        if result:
            print("\n" + "=" * 60)
            print("Demo completed successfully!")
            print("=" * 60)
    else:
        print(f"Sample PDF not found at: {sample_pdf}")
        print("\nTo test with your own PDF, run:")
        print('  python -c "from demo_upload import demo_upload; demo_upload(\'your_file.pdf\')"')

if __name__ == "__main__":
    main()
