import os
import time
import xml.etree.ElementTree as ET
from hashlib import md5
from pathlib import Path
from typing import Any, Dict, List

import backoff
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_mistralai import MistralAIEmbeddings
from loguru import logger
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Constants
EMBEDDING_BATCH_SIZE = 10  # Batch size for embedding API calls
PROCESSING_BATCH_SIZE = 100  # Increased batch size for processing documents
MAX_WORKERS = 1  # Fewer workers to reduce concurrent API calls
MAX_DOCUMENTS = 2  # Process fewer documents for debugging
CHUNK_SIZE = 1000  # Larger chunks to reduce total number of documents
CHUNK_OVERLAP = 100  # Smaller overlap
BATCH_DELAY = 2  # Delay between batches in seconds
MAX_RETRIES = 3  # Maximum number of retries for rate-limited requests


class XMLParserDebug:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.initial_doc_count = 0

        # Validate data directory exists
        if not self.data_dir.exists():
            raise ValueError(f"Data directory does not exist: {self.data_dir}")

        # Validate data directory contains XML files
        xml_files = list(self.data_dir.rglob("*.xml"))
        if not xml_files:
            raise ValueError(f"No XML files found in {self.data_dir}")

        logger.info(f"Found {len(xml_files)} XML files in {self.data_dir}")

        # Use larger chunks to reduce total number of documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )

        # Initialize embeddings with retry logic
        self.embeddings = MistralAIEmbeddings(
            model="mistral-embed",
            api_key=os.getenv("MISTRAL_API_KEY"),
            max_retries=MAX_RETRIES,
        )

        # Create chroma_db directory if it doesn't exist
        persist_dir = Path("chroma_db")
        persist_dir.mkdir(exist_ok=True)

        # Initialize vector store
        self.vector_store = Chroma(
            collection_name="service_public",
            embedding_function=self.embeddings,
            persist_directory=str(persist_dir),
        )

        # Get initial document count
        self.initial_doc_count = self.vector_store._collection.count()
        logger.info(f"Initial document count in vector store: {self.initial_doc_count}")

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
            logger.debug(f"Processing file: {file_path}")
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
            logger.debug(f"Created {len(chunks)} chunks for {file_path}")

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

            logger.success(
                f"Successfully processed {file_path} into {len(documents)} documents"
            )
            return documents

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return []

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=MAX_RETRIES,
        giveup=lambda e: "429" not in str(e),
    )
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a batch of texts with retry logic."""
        try:
            logger.debug(f"Getting embeddings for batch of {len(texts)} texts")
            embeddings = self.embeddings.embed_documents(texts)
            logger.success(f"Successfully got embeddings for {len(embeddings)} texts")
            return embeddings
        except Exception as e:
            if "429" in str(e):
                logger.warning(
                    f"Rate limit hit while getting embeddings, retrying: {str(e)}"
                )
                raise
            logger.error(f"Error getting embeddings: {str(e)}")
            raise

    def process_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Process a batch of documents by getting embeddings in larger batches."""
        if not batch:
            return

        # Split the batch into smaller groups for embedding
        texts = [doc["content"] for doc in batch]
        metadatas = [doc["metadata"] for doc in batch]
        
        # Generate unique IDs for each document
        hash_ids = [md5(text.encode()).hexdigest() for text in texts]
        ids = [f"doc_{i}_{hash_id}" for i, hash_id in enumerate(hash_ids)]

        # Process all embeddings in one batch if possible, otherwise in chunks
        all_embeddings = []
        logger.info(f"Processing {len(texts)} texts in {len(texts) // EMBEDDING_BATCH_SIZE} batches")
        for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
            batch_texts = texts[i : i + EMBEDDING_BATCH_SIZE]
            try:
                batch_embeddings = self.get_embeddings_batch(batch_texts)
                all_embeddings.extend(batch_embeddings)
                logger.success(f"Successfully got embeddings for {len(batch_embeddings)} texts")
                if i + EMBEDDING_BATCH_SIZE < len(texts):  # Only sleep if there are more batches
                    time.sleep(BATCH_DELAY)
            except Exception as e:
                logger.error(f"Failed to get embeddings for batch: {str(e)}")
                raise

        try:
            # Add all documents to vector store in one batch
            logger.debug(
                f"Adding {len(batch)} documents to vector store with pre-computed embeddings"
            )
            self.vector_store._collection.add(
                ids=ids,
                embeddings=all_embeddings,
                documents=texts,
                metadatas=metadatas
            )

            # Verify the batch was added
            current_count = self.vector_store._collection.count()
            logger.info(f"Current document count after batch: {current_count}")

        except Exception as e:
            logger.error(f"Error adding batch to vector store: {str(e)}")
            raise

    def process_directory(self):
        """Process a limited number of XML files in the data directory."""
        xml_files = list(self.data_dir.rglob("*.xml"))[:MAX_DOCUMENTS]
        logger.info(f"Processing first {len(xml_files)} XML files for debugging")

        # Process XML files in sequential order
        all_documents = []
        for file_path in tqdm(xml_files, desc="Processing XML files"):
            try:
                documents = self.process_xml_file(file_path)
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")

        logger.info(f"Processed {len(all_documents)} total chunks")

        # Process documents in larger batches
        for i in tqdm(
            range(0, len(all_documents), PROCESSING_BATCH_SIZE),
            desc="Adding to vector store",
        ):
            batch = all_documents[i : i + PROCESSING_BATCH_SIZE]
            try:
                self.process_batch(batch)
                logger.info(
                    f"Processed batch {i // PROCESSING_BATCH_SIZE + 1}/{(len(all_documents) - 1) // PROCESSING_BATCH_SIZE + 1}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to process batch after {MAX_RETRIES} retries: {str(e)}"
                )
                continue

        # Final verification
        final_doc_count = self.vector_store._collection.count()
        added_docs = final_doc_count - self.initial_doc_count
        logger.info(f"Initial document count: {self.initial_doc_count}")
        logger.info(f"Final document count: {final_doc_count}")
        logger.info(f"Total documents added: {added_docs}")
        logger.info(f"Expected documents to add: {len(all_documents)}")

        if added_docs != len(all_documents):
            logger.error(
                f"Document count mismatch! Expected to add {len(all_documents)} but added {added_docs}"
            )
        else:
            logger.success("Success! All documents were added correctly.")


def main():
    # Use the correct path to the XML files
    parser = XMLParserDebug("data/service-public")
    parser.process_directory()


if __name__ == "__main__":
    main()
