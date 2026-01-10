"""Utility functions for file handling in Maven dependency analysis."""

import json
from pathlib import Path
from typing import Union, Dict, Any


def validate_json_file(file_path: Union[str, Path]) -> bool:
    """
    Validate that a file is a valid JSON file.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if the file is valid JSON, False otherwise
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        
        return True
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return False


def validate_text_file(file_path: Union[str, Path]) -> bool:
    """
    Validate that a file is a readable text file.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if the file is readable text, False otherwise
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)  # Read first 1KB to check if it's text
        
        return True
    except (UnicodeDecodeError, OSError):
        return False


def safe_read_file(file_path: Union[str, Path], fallback_encoding: str = 'latin1') -> str:
    """
    Safely read a file with fallback encodings.
    
    Args:
        file_path: Path to the file to read
        fallback_encoding: Encoding to try if utf-8 fails
        
    Returns:
        File content as string
    """
    file_path = Path(file_path)
    
    # Try common encodings
    encodings = ['utf-8', 'utf-8-sig', fallback_encoding]
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, raise an exception
    raise ValueError(f"Could not decode file {file_path} with any of the attempted encodings")


def ensure_output_directory(output_path: Union[str, Path]) -> Path:
    """
    Ensure that the output directory exists.
    
    Args:
        output_path: Path to the output file/directory
        
    Returns:
        Path object for the output directory
    """
    output_path = Path(output_path)
    output_dir = output_path.parent if output_path.suffix else output_path
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir