# Colbert Database

This directory contains the database processing and vector store management for Colbert. It handles the ingestion, processing, and storage of French public administration data into a vector database for efficient semantic search.

## Overview

The database module provides:
- Automated download of official French administration data
- XML parsing and processing of service-public.fr content
- Vector database management using ChromaDB
- Data ingestion pipeline for RAG system
- Testing utilities for vector search

## Technical Stack

- **Vector Database**: ChromaDB
- **AI/ML**: 
  - LangChain
  - Mistral AI (for embeddings)
- **Data Processing**: 
  - Python XML processing
  - TQDM for progress tracking
- **Python Version**: 3.13+

## Project Structure

```
database/
├── chroma_db/              # Vector database storage
├── data/                   # Raw and processed data
├── parse_xml_dump_v2.py    # Main XML processing script
├── download.py             # Data download utilities
├── test_vector_db.py       # Vector DB testing
├── test_colbert_vector.py  # Colbert-specific vector tests
└── test_parse_xml.ipynb    # XML parsing notebook
```

## Data Sources

The system downloads and processes data from:
- Service-Public.fr XML dumps
  - Vosdroits dataset (latest)
  - Schema definitions
- Data is sourced from data.gouv.fr

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `MISTRAL_API_KEY`: Your Mistral AI API key
- `CHROMA_DB_PATH`: Path to ChromaDB storage

## Usage

### Downloading Data

To download the latest data from service-public.fr:
```bash
python download.py
```

This will:
1. Download the latest XML dumps
2. Extract them to the `data/` directory
3. Clean up temporary files

### Processing Data

To process the downloaded XML data:
```bash
python parse_xml_dump_v2.py
```

This will:
1. Parse the XML files
2. Process the content
3. Generate embeddings
4. Store in ChromaDB

### Testing

Run the vector database tests:
```bash
python test_vector_db.py
```

For interactive testing and development:
1. Start Jupyter:
```bash
jupyter notebook
```
2. Open `test_parse_xml.ipynb`

## Data Flow

1. **Download**: Raw XML data is downloaded from data.gouv.fr
2. **Parse**: XML files are parsed and structured
3. **Process**: Content is cleaned and prepared
4. **Embed**: Text is converted to vector embeddings
5. **Store**: Vectors are stored in ChromaDB
6. **Index**: Efficient search indexes are created

## Vector Database

The system uses ChromaDB for vector storage with:
- Persistent storage in `chroma_db/` directory
- Efficient similarity search
- Metadata filtering capabilities
- Automatic index management

## Development

For development and testing:
1. Use the Jupyter notebook for interactive testing
2. Run unit tests for vector operations
3. Check logs for processing status
4. Monitor vector database performance

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0) license.
