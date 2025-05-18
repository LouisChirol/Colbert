import logging
import os
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_mistralai import MistralAIEmbeddings
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
BATCH_SIZE = 100  # Number of documents to process in each batch
MAX_WORKERS = 8  # Number of parallel workers for XML processing


class XMLParser:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)

        # Validate data directory exists
        if not self.data_dir.exists():
            raise ValueError(f"Data directory does not exist: {self.data_dir}")

        # Validate data directory contains XML files
        xml_files = list(self.data_dir.rglob("*.xml"))
        if not xml_files:
            raise ValueError(f"No XML files found in {self.data_dir}")

        logger.info(f"Found {len(xml_files)} XML files in {self.data_dir}")

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        # Initialize embeddings
        self.embeddings = MistralAIEmbeddings(
            model="mistral-embed", api_key=os.getenv("MISTRAL_API_KEY")
        )

        # Initialize vector store
        self.vector_store = Chroma(
            collection_name="service_public",
            embedding_function=self.embeddings,
            persist_directory="chroma_db",
        )

    def extract_text_content(self, element: ET.Element) -> str:
        """Extract text content from XML element and its children."""
        text_parts = []

        # Extract text from the current element
        if element.text and element.text.strip():
            text_parts.append(element.text.strip())

        # Process child elements
        for child in element:
            if child.text and child.text.strip():
                text_parts.append(child.text.strip())
            text_parts.extend(self.extract_text_content(child))

        return " ".join(text_parts)

    def extract_metadata(self, element: ET.Element) -> Dict[str, Any]:
        """Extract metadata from XML element."""
        metadata = {}

        # Extract Dublin Core metadata
        for dc_elem in element.findall(".//{http://purl.org/dc/elements/1.1/}*"):
            tag = dc_elem.tag.split("}")[-1]
            metadata[tag] = dc_elem.text

        # Extract other important attributes
        for attr in element.attrib:
            if attr in ["ID", "type", "spUrl", "dateCreation", "dateMaj"]:
                metadata[attr] = element.attrib[attr]

        return metadata

    def process_xml_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a single XML file and return chunks with metadata."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Extract main content
            content = self.extract_text_content(root)
            metadata = self.extract_metadata(root)

            # Skip if content is empty
            if not content.strip():
                logger.warning(f"Skipping {file_path}: Empty content")
                return []

            # Add file information to metadata
            metadata["source_file"] = str(file_path)

            # Split content into chunks
            chunks = self.text_splitter.split_text(content)

            # Skip if no chunks were created
            if not chunks:
                logger.warning(f"Skipping {file_path}: No chunks created")
                return []

            # Create documents with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                if not chunk.strip():  # Skip empty chunks
                    continue
                doc = {
                    "content": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_id": i,
                        "total_chunks": len(chunks),
                    },
                }
                documents.append(doc)

            return documents

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return []

    def process_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Process a batch of documents and add them to the vector store."""
        if not batch:
            return

        texts = [doc["content"] for doc in batch]
        metadatas = [doc["metadata"] for doc in batch]

        try:
            self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        except Exception as e:
            logger.error(f"Error adding batch to vector store: {str(e)}")

    def process_directory(self):
        """Process all XML files in the data directory."""
        xml_files = list(self.data_dir.rglob("*.xml"))
        logger.info(f"Found {len(xml_files)} XML files to process")

        # Process XML files in parallel
        all_documents = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_file = {
                executor.submit(self.process_xml_file, file_path): file_path
                for file_path in xml_files
            }

            for future in tqdm(
                as_completed(future_to_file),
                total=len(xml_files),
                desc="Processing XML files",
            ):
                file_path = future_to_file[future]
                try:
                    documents = future.result()
                    all_documents.extend(documents)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")

        logger.info(f"Processed {len(all_documents)} total chunks")

        # Process documents in batches
        for i in tqdm(
            range(0, len(all_documents), BATCH_SIZE), desc="Adding to vector store"
        ):
            batch = all_documents[i: i + BATCH_SIZE]
            self.process_batch(batch)

        # Persist the database
        self.vector_store.persist()
        logger.info("Vector database persisted successfully")


def main():
    # Use the correct path to the XML files
    parser = XMLParser("data/service-public/vosdroits-latest")
    parser.process_directory()


if __name__ == "__main__":
    main()
