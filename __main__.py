#!/usr/bin/env python3
"""
FlashRAG - Simple but solid RAG system
Main entry point
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from chat import main

if __name__ == "__main__":
    main()