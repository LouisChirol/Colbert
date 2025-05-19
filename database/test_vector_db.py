import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_mistralai import MistralAIEmbeddings

# Load environment variables
load_dotenv()


def test_vector_db():
    # Initialize embeddings
    embeddings = MistralAIEmbeddings(
        model="mistral-embed", api_key=os.getenv("MISTRAL_API_KEY")
    )

    # Load the existing vector store
    vector_store = Chroma(
        collection_name="service_public",
        embedding_function=embeddings,
        persist_directory="chroma_db",
    )

    # Test query
    test_query = "Comment obtenir un permis de construire ?"
    print(f"\nTesting query: {test_query}")

    # Get similar documents
    docs = vector_store.similarity_search(test_query, k=3)

    print("\nFound documents:")
    for i, doc in enumerate(docs, 1):
        print(f"\n--- Document {i} ---")
        print(f"Content: {doc.page_content[:200]}...")  # First 200 chars
        print(f"Metadata: {doc.metadata}")


if __name__ == "__main__":
    test_vector_db()
