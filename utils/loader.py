from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path


def load_pdf(pdf_path: str):
    """
    Load a PDF and return documents.
    """

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    loader = PyPDFLoader(str(path))
    documents = loader.load()

    return documents