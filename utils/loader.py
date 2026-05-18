from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path


def load_pdf(pdf_path: str):
    """
    Load a PDF and return documents.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List[Document]: Loaded documents
        
    Raises:
        FileNotFoundError: If PDF doesn't exist
        RuntimeError: If PDF loading fails
    """
    
    path = Path(pdf_path).resolve()
    
    if not path.exists():
        raise FileNotFoundError(
            f"❌ PDF not found: {pdf_path}\n"
            f"Expected at: {path}"
        )
    
    if not path.suffix.lower() == ".pdf":
        raise ValueError(f"❌ Not a PDF file: {path.suffix}")
    
    try:
        loader = PyPDFLoader(str(path))
        documents = loader.load()
        
        if not documents:
            raise ValueError("❌ PDF loaded but contains no pages")
        
        print(f"✅ Loaded PDF: {path.name} ({len(documents)} pages)")
        return documents
        
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load PDF: {str(e)}")