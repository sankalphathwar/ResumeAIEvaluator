import PyPDF2
import docx2txt
import os

def parse_resume(file_path):
    """
    Parse resume content from various file formats (PDF, DOCX, TXT)
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        str: Extracted text from the resume
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_extension == '.pdf':
            return parse_pdf(file_path)
        elif file_extension == '.docx':
            return parse_docx(file_path)
        elif file_extension == '.txt':
            return parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    except Exception as e:
        raise Exception(f"Error parsing file: {str(e)}")

def parse_pdf(pdf_path):
    """
    Extract text from PDF file
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
                
        # Clean up text
        text = ' '.join(text.split())
        return text
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")

def parse_docx(docx_path):
    """
    Extract text from DOCX file
    
    Args:
        docx_path (str): Path to the DOCX file
        
    Returns:
        str: Extracted text
    """
    try:
        text = docx2txt.process(docx_path)
        
        # Clean up text
        text = ' '.join(text.split())
        return text
    except Exception as e:
        raise Exception(f"Error parsing DOCX: {str(e)}")

def parse_txt(txt_path):
    """
    Extract text from TXT file
    
    Args:
        txt_path (str): Path to the TXT file
        
    Returns:
        str: Extracted text
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            text = file.read()
            
        # Clean up text
        text = ' '.join(text.split())
        return text
    except UnicodeDecodeError:
        # Try with different encoding if utf-8 fails
        with open(txt_path, 'r', encoding='latin-1') as file:
            text = file.read()
            
        # Clean up text
        text = ' '.join(text.split())
        return text
    except Exception as e:
        raise Exception(f"Error parsing TXT: {str(e)}")
