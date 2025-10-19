#!/usr/bin/env python3
"""Test script to render templates and compile PDFs without running full pipeline."""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from template_renderer import TemplateRenderer
from utils import compile_latex_to_pdf

def test_resume_rendering():
    """Test resume template rendering and PDF compilation."""
    print("=" * 80)
    print("Testing Resume Template Rendering")
    print("=" * 80)
    
    # Load the existing Resume.json
    json_path = Path("output/Microsoft_Software Engineer_MSFT1891711/Resume.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        resume_data = json.load(f)
    
    print(f"\n✓ Loaded resume JSON from {json_path}")
    
    # Initialize renderer
    renderer = TemplateRenderer()
    print("✓ Initialized TemplateRenderer")
    
    # Render the resume
    print("\nRendering resume template...")
    try:
        resume_latex = renderer.render_resume(resume_data)
        print("✓ Resume template rendered successfully")
    except Exception as e:
        print(f"✗ Error rendering resume template: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Save the LaTeX
    output_dir = Path("output/Microsoft_Software Engineer_MSFT1891711")
    tex_path = output_dir / "Resume_test.tex"
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(resume_latex)
    print(f"✓ Saved LaTeX to {tex_path}")
    
    # Compile to PDF
    print("\nCompiling resume PDF...")
    try:
        pdf_path = compile_latex_to_pdf(str(tex_path), str(output_dir))
        print(f"✓ Resume PDF compiled successfully: {pdf_path}")
        return True
    except Exception as e:
        print(f"✗ Error compiling resume PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cover_letter_rendering():
    """Test cover letter template rendering and PDF compilation."""
    print("\n" + "=" * 80)
    print("Testing Cover Letter Template Rendering")
    print("=" * 80)
    
    # Load the existing Resume.json for contact info
    json_path = Path("output/Microsoft_Software Engineer_MSFT1891711/Resume.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        resume_data = json.load(f)
    contact_info = resume_data['contact_info']
    
    # Load the cover letter text
    cl_path = Path("output/Microsoft_Software Engineer_MSFT1891711/CoverLetter.txt")
    with open(cl_path, 'r', encoding='utf-8') as f:
        cover_letter_text = f.read()
    
    print(f"\n✓ Loaded contact info and cover letter text")
    
    # Initialize renderer
    renderer = TemplateRenderer()
    print("✓ Initialized TemplateRenderer")
    
    # Render the cover letter
    print("\nRendering cover letter template...")
    try:
        cl_latex = renderer.render_cover_letter(contact_info, cover_letter_text)
        print("✓ Cover letter template rendered successfully")
    except Exception as e:
        print(f"✗ Error rendering cover letter template: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Save the LaTeX
    output_dir = Path("output/Microsoft_Software Engineer_MSFT1891711")
    tex_path = output_dir / "CoverLetter_test.tex"
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(cl_latex)
    print(f"✓ Saved LaTeX to {tex_path}")
    
    # Compile to PDF
    print("\nCompiling cover letter PDF...")
    try:
        pdf_path = compile_latex_to_pdf(str(tex_path), str(output_dir))
        print(f"✓ Cover letter PDF compiled successfully: {pdf_path}")
        return True
    except Exception as e:
        print(f"✗ Error compiling cover letter PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_referral_rendering():
    """Test referral resume and cover letter rendering."""
    print("\n" + "=" * 80)
    print("Testing Referral Template Rendering")
    print("=" * 80)
    
    # Load the existing Resume.json
    json_path = Path("output/Microsoft_Software Engineer_MSFT1891711/Resume.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        resume_data = json.load(f)
    
    # Load the cover letter text
    cl_path = Path("output/Microsoft_Software Engineer_MSFT1891711/CoverLetter.txt")
    with open(cl_path, 'r', encoding='utf-8') as f:
        cover_letter_text = f.read()
    
    # Mock referral contact (using same contact for testing)
    referral_contact = {
        'first_name': 'John',
        'last_name': 'Doe',
        'phone': '+1 555-123-4567',
        'email': 'john.doe@example.com',
        'linkedin_url': 'https://linkedin.com/in/johndoe',
        'github_url': 'https://github.com/johndoe'
    }
    
    print(f"\n✓ Loaded resume data and cover letter text")
    print(f"✓ Using test referral contact: {referral_contact['first_name']} {referral_contact['last_name']}")
    
    # Initialize renderer
    renderer = TemplateRenderer()
    print("✓ Initialized TemplateRenderer")
    
    # Render referral resume
    print("\nRendering referral resume template...")
    try:
        resume_latex = renderer.render_resume_with_referral(resume_data, referral_contact)
        print("✓ Referral resume template rendered successfully")
    except Exception as e:
        print(f"✗ Error rendering referral resume template: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Save and compile referral resume
    output_dir = Path("output/Microsoft_Software Engineer_MSFT1891711")
    tex_path = output_dir / "Resume_referral_test.tex"
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(resume_latex)
    print(f"✓ Saved referral resume LaTeX to {tex_path}")
    
    print("\nCompiling referral resume PDF...")
    try:
        pdf_path = compile_latex_to_pdf(str(tex_path), str(output_dir))
        print(f"✓ Referral resume PDF compiled successfully: {pdf_path}")
    except Exception as e:
        print(f"✗ Error compiling referral resume PDF: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Render referral cover letter
    print("\nRendering referral cover letter template...")
    try:
        cl_latex = renderer.render_cover_letter_with_referral(cover_letter_text, referral_contact)
        print("✓ Referral cover letter template rendered successfully")
    except Exception as e:
        print(f"✗ Error rendering referral cover letter template: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Save and compile referral cover letter
    tex_path = output_dir / "CoverLetter_referral_test.tex"
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(cl_latex)
    print(f"✓ Saved referral cover letter LaTeX to {tex_path}")
    
    print("\nCompiling referral cover letter PDF...")
    try:
        pdf_path = compile_latex_to_pdf(str(tex_path), str(output_dir))
        print(f"✓ Referral cover letter PDF compiled successfully: {pdf_path}")
        return True
    except Exception as e:
        print(f"✗ Error compiling referral cover letter PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\nStarting template rendering tests...\n")
    
    resume_success = test_resume_rendering()
    cl_success = test_cover_letter_rendering()
    referral_success = test_referral_rendering()
    
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Resume: {'✓ PASS' if resume_success else '✗ FAIL'}")
    print(f"Cover Letter: {'✓ PASS' if cl_success else '✗ FAIL'}")
    print(f"Referral (Resume + Cover Letter): {'✓ PASS' if referral_success else '✗ FAIL'}")
    print()
    
    sys.exit(0 if (resume_success and cl_success and referral_success) else 1)
