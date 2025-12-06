"""
File loader utility for handling multiple file formats.
Supports: .py, .cpp, .java, .c, .js, .ipynb, and more.
"""

import json
import io
import pypdf
from typing import Dict, Optional

def load_code_file(file_path: str) -> Dict[str, str]:
    """
    Loads code from various file formats.
    
    Returns:
        Dict with 'content' (str) and 'language' (str)
    """
    result = {
        "content": "",
        "language": "unknown",
        "error": None
    }
    
    try:
        # Jupyter Notebook
        if file_path.endswith('.ipynb'):
            with open(file_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)
                code_cells = []
                for cell in notebook.get('cells', []):
                    if cell.get('cell_type') == 'code':
                        code_cells.append(''.join(cell.get('source', [])))
                
                result['content'] = '\n\n'.join(code_cells)
                result['language'] = 'python'
        
        # Python
        elif file_path.endswith('.py'):
            with open(file_path, 'r', encoding='utf-8') as f:
                result['content'] = f.read()
                result['language'] = 'python'
        
        # C++
        elif file_path.endswith(('.cpp', '.cc', '.cxx', '.hpp', '.h')):
            with open(file_path, 'r', encoding='utf-8') as f:
                result['content'] = f.read()
                result['language'] = 'cpp'
        
        # C
        elif file_path.endswith('.c'):
            with open(file_path, 'r', encoding='utf-8') as f:
                result['content'] = f.read()
                result['language'] = 'c'
        
        # Java
        elif file_path.endswith('.java'):
            with open(file_path, 'r', encoding='utf-8') as f:
                result['content'] = f.read()
                result['language'] = 'java'
        
        # JavaScript
        elif file_path.endswith('.js'):
            with open(file_path, 'r', encoding='utf-8') as f:
                result['content'] = f.read()
                result['language'] = 'javascript'

        # PDF
        elif file_path.endswith('.pdf'):
            try:
                reader = pypdf.PdfReader(file_path)
                text = ""
                num_pages = len(reader.pages)
                extraction_method = 'standard'
                
                print(f"📄 Extracting {num_pages} pages from PDF...")
                
                for page_num, page in enumerate(reader.pages):
                    try:
                        # Try standard extraction first
                        page_text = page.extract_text()
                        
                        # If extraction is poor, try alternative method
                        if len(page_text.strip()) < 50:
                            try:
                                # Try with layout preservation
                                page_text = page.extract_text(extraction_mode="layout")
                                extraction_method = 'layout'
                            except:
                                pass
                        
                        text += page_text + '\n'
                        
                    except Exception as page_error:
                        print(f"⚠️ Page {page_num + 1} extraction warning: {page_error}")
                        text += f"[Page {page_num + 1} extraction issue]\n"
                
                # Validate extraction quality
                content_length = len(text.strip())
                print(f"✅ Extracted {content_length} characters using {extraction_method} method")
                
                # Check if we got meaningful content
                if content_length < 100:
                    warning_msg = (
                        f"⚠️ WARNING: PDF yielded only {content_length} characters.\n"
                        f"This may indicate:\n"
                        f"  - Image-based PDF (scanned document)\n"
                        f"  - Encrypted/protected PDF\n"
                        f"  - Empty or corrupted PDF\n\n"
                    )
                    print(warning_msg)
                    result['content'] = text
                    result['error'] = warning_msg.strip()
                elif content_length < 500:
                    print(f"⚠️ Low text content ({content_length} chars) - may be incomplete")
                    result['content'] = text
                else:
                    print(f"✅ Good extraction quality ({content_length} characters)")
                    result['content'] = text
                
                result['language'] = 'text'
                
            except Exception as e:
                error_msg = (
                    f"PDF extraction error: {str(e)}\n"
                    f"Please ensure the PDF:\n"
                    f"  - Is not password-protected or encrypted\n"
                    f"  - Contains actual text (not just images)\n"
                    f"  - Is not corrupted"
                )
                print(f"❌ {error_msg}")
                result['error'] = error_msg
        
        # Generic text file
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                result['content'] = f.read()
                result['language'] = 'text'
    
    except Exception as e:
        result['error'] = str(e)
    
    return result


def extract_from_streamlit_upload(uploaded_file) -> Dict[str, str]:
    """
    Extracts content from Streamlit's UploadedFile object.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        Dict with 'content' and 'language'
    """
    result = {
        "content": "",
        "language": "unknown",
        "error": None
    }
    
    try:
        file_name = uploaded_file.name
        
        # Jupyter Notebook
        if file_name.endswith('.ipynb'):
            notebook = json.load(uploaded_file)
            code_cells = []
            for cell in notebook.get('cells', []):
                if cell.get('cell_type') == 'code':
                    code_cells.append(''.join(cell.get('source', [])))
            
            result['content'] = '\n\n'.join(code_cells)
            result['language'] = 'python'
        
        # PDF
        elif file_name.endswith('.pdf'):
            try:
                # Streamlit UploadedFile is a BytesIO-like object
                reader = pypdf.PdfReader(uploaded_file)
                text = ""
                num_pages = len(reader.pages)
                extraction_method = 'standard'
                
                print(f"📄 Extracting {num_pages} pages from {file_name}...")
                
                for page_num, page in enumerate(reader.pages):
                    try:
                        # Try standard extraction first
                        page_text = page.extract_text()
                        
                        # If extraction is poor, try alternative method
                        if len(page_text.strip()) < 50:
                            try:
                                # Try with layout preservation
                                page_text = page.extract_text(extraction_mode="layout")
                                extraction_method = 'layout'
                            except:
                                pass
                        
                        text += page_text + '\n'
                        
                    except Exception as page_error:
                        print(f"⚠️ Page {page_num + 1} extraction warning: {page_error}")
                        text += f"[Page {page_num + 1} extraction issue]\n"
                
                # Validate extraction quality
                content_length = len(text.strip())
                print(f"✅ Extracted {content_length} characters from {file_name} using {extraction_method} method")
                
                # Check if we got meaningful content
                if content_length < 100:
                    warning_msg = (
                        f"⚠️ WARNING: PDF '{file_name}' yielded only {content_length} characters.\n"
                        f"This may indicate:\n"
                        f"  - Image-based PDF (scanned document)\n"
                        f"  - Encrypted/protected PDF\n"
                        f"  - Empty or corrupted PDF\n\n"
                    )
                    print(warning_msg)
                    result['content'] = text
                    result['error'] = warning_msg.strip()
                elif content_length < 500:
                    print(f"⚠️ Low text content ({content_length} chars) - may be incomplete")
                    result['content'] = text
                else:
                    print(f"✅ Good extraction quality ({content_length} characters)")
                    result['content'] = text
                
                result['language'] = 'text'
                
            except Exception as e:
                error_msg = (
                    f"PDF extraction error: {str(e)}\n"
                    f"Please ensure the PDF:\n"
                    f"  - Is not password-protected or encrypted\n"
                    f"  - Contains actual text (not just images)\n"
                    f"  - Is not corrupted"
                )
                print(f"❌ PDF error for {file_name}: {error_msg}")
                result['error'] = error_msg
        
        # Text-based files
        else:
            content = uploaded_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            result['content'] = content
            
            # Detect language
            if file_name.endswith('.py'):
                result['language'] = 'python'
            elif file_name.endswith(('.cpp', '.cc', '.cxx', '.hpp', '.h')):
                result['language'] = 'cpp'
            elif file_name.endswith('.c'):
                result['language'] = 'c'
            elif file_name.endswith('.java'):
                result['language'] = 'java'
            elif file_name.endswith('.js'):
                result['language'] = 'javascript'
            else:
                result['language'] = 'text'
    
    except Exception as e:
        result['error'] = str(e)
    
    return result
