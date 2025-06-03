import os
import re
from collections import defaultdict
from pathlib import Path

from colbert_prompt import COLBERT_PROMPT, OUTPUT_PROMPT
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from loguru import logger
from pydantic import BaseModel, Field
from redis_service import RedisService

load_dotenv()


MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is not set")

MISTRAL_MODELS = ["mistral-medium", "mistral-small"]

# RAG parameters
TOP_K_RETRIEVAL = 10  # Match test scripts for consistency
TOP_N_SOURCES = 4  # Keep same as TOP_K_RETRIEVAL

# Paths
WORKSPACE_ROOT = Path(__file__).parent.parent
CHROMA_DB_PATH = WORKSPACE_ROOT / "database" / "chroma_db"


class ColbertResponse(BaseModel):
    answer: str = Field(description="The answer to the user's question")
    sources: list[str] = Field(
        description="The sources used to answer the user's question, should be a list of urls"
    )
    secondary_sources: list[str] = Field(
        description="The secondary sources used to answer the user's question, should be a list of urls"
    )


class ColbertAgent:
    def __init__(self):
        # Initialize Redis service
        self.redis_service = RedisService()

        # No web search tools; only use vector database
        self.tools = []

        # Initialize vector store
        self.embeddings = MistralAIEmbeddings(
            model="mistral-embed",
            api_key=MISTRAL_API_KEY
        )
        
        # Ensure the chroma_db directory exists
        CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
        
        # Initialize vector store with the correct path
        self.vector_store = Chroma(
            collection_name="service_public",
            embedding_function=self.embeddings,
            persist_directory=str(CHROMA_DB_PATH)
        )

        # Log initial document count
        self.doc_count = self.vector_store._collection.count()
        logger.info(f"Initialized Chroma DB with {self.doc_count} documents at {CHROMA_DB_PATH}")

        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", COLBERT_PROMPT),
                ("system", OUTPUT_PROMPT),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

        # Initialize with the first model
        self._initialize_llm(MISTRAL_MODELS[0])

    def _initialize_llm(self, model_name: str):
        """Initialize the LLM with the specified model."""
        self.llm = ChatMistralAI(
            model=model_name,
            temperature=0.7,
            max_retries=2,
            api_key=MISTRAL_API_KEY,
        )

        # Create a prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", COLBERT_PROMPT),
                ("system", OUTPUT_PROMPT),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
                ("human", "{context}"),
            ]
        )

        # Create the agent with structured output using the prompt
        self.agent = self.llm.with_structured_output(ColbertResponse)
        
        # Chain the prompt with the structured output agent
        self.chain = self.prompt | self.agent
        
        # Setup history
        self.chain_with_history = RunnableWithMessageHistory(
            self.chain,
            self.get_redis_history,
            input_messages_key="input",
            history_messages_key="history",
            context_messages_key="context",
        )

    def get_redis_history(self, session_id: str):
        history = self.redis_service.get_history(session_id)
        logger.debug(f"History: {history}")
        return history

    def _strip_code_blocks(self, text: str) -> str:
        """Remove Markdown code block formatting from a string."""
        # Remove triple backtick code blocks
        text = re.sub(r'```[a-zA-Z]*\n?', '', text)
        text = text.replace('```', '')
        # Remove single backtick inline code
        text = text.replace('`', '')
        return text.strip()

    def _format_response(self, response: ColbertResponse) -> str:
        """Format the response with sources using markdown."""
        # Format the answer with proper spacing and line breaks
        formatted_answer = self._strip_code_blocks(response.answer.strip())

        # Format sources as markdown links with prefix
        if response.sources:
            sources_text = "\n\nSources:\n"
            for source in response.sources:
                sources_text += f"- [{source}]({source})\n"
            formatted_answer += sources_text

        return formatted_answer

    def _get_relevant_documents(self, query: str) -> dict[str, list[dict]]:
        """Retrieve relevant documents, deduplicated by source, with their metadata.
        
        Returns a dictionary mapping source URLs to lists of document chunks with their metadata.
        """
        logger.info(f"Searching for documents with query: {query}")
        
        # Use similarity_search like the test scripts
        docs = self.vector_store.similarity_search(query, k=TOP_K_RETRIEVAL)
        logger.info(f"Found {len(docs)} documents in similarity search")
        
        # Group documents by source URL
        source_docs: dict[str, list[dict]] = defaultdict(list)
        for i, doc in enumerate(docs, 1):
            # Get the source URL from metadata, with fallback to service-public.fr
            source_url = doc.metadata.get('spUrl')
            source_metadata = doc.metadata.get('source')
            
            if not source_url and source_metadata:
                # If no spUrl but we have a source, use it
                source_url = source_metadata
                logger.debug(f"Using source metadata URL: {source_url}")
            elif not source_url:
                # If no spUrl, try to construct a service-public.fr URL from the ID
                doc_id = doc.metadata.get('ID')
                if doc_id:
                    source_url = f"https://www.service-public.fr/particuliers/vosdroits/{doc_id}"
                    logger.debug(f"Constructed service-public.fr URL from ID {doc_id}")
                else:
                    source_url = "https://www.service-public.fr"
                    logger.debug("Using fallback service-public.fr URL")
            
            # Store both URLs in metadata for reference
            doc_metadata = {
                **doc.metadata,
                'primary_source': source_url,
                'secondary_source': source_metadata if source_metadata != source_url else None
            }
            
            source_docs[source_url].append({
                'content': doc.page_content,
                'metadata': doc_metadata
            })
            logger.debug(f"Document {i} from source: {source_url}")
            if source_metadata and source_metadata != source_url:
                logger.debug(f"Additional source metadata: {source_metadata}")
            logger.debug(f"Content preview: {doc.page_content[:200]}...")
        
        logger.info(f"Grouped documents into {len(source_docs)} unique sources")
        for source, docs in source_docs.items():
            logger.info(f"Source {source}: {len(docs)} documents")
            # Log additional source metadata if available
            for doc in docs:
                if doc['metadata'].get('secondary_source'):
                    logger.debug(f"Document also has source: {doc['metadata']['secondary_source']}")
        
        return dict(source_docs)

    def _format_context(self, source_docs: dict[str, list[dict]]) -> str:
        """Format the context from deduplicated documents for the LLM."""
        context_parts = []
        
        for source_url, docs in source_docs.items():
            # Get all content from this source
            content = "\n".join(doc['content'] for doc in docs)
            context_parts.append(f"Source: {source_url}\nContent:\n{content}\n")
         
        return "\n---\n".join(context_parts)

    def _get_source_urls(self, source_docs: dict[str, list[dict]]) -> tuple[list[str], list[str]]:
        """Extract unique source URLs from the documents, including both primary and secondary sources."""
        sources = set()
        secondary_sources = set()
        for docs in source_docs.values():
            for doc in docs:
                # Add primary source
                if doc['metadata'].get('primary_source'):
                    sources.add(doc['metadata']['primary_source'])
                # Add secondary source if it exists and is different
                if doc['metadata'].get('secondary_source'):
                    secondary_sources.add(doc['metadata']['secondary_source'])
        # Convert to list and ensure service-public.fr is last if present
        source_list = list(sources)
        secondary_source_list = list(secondary_sources)
        
        logger.info(f"Extracted {len(source_list)} unique sources including secondary sources")
        return source_list, secondary_source_list

    def ask_colbert(self, message: str, session_id: str) -> str:

        # Get relevant documents
        source_docs = self._get_relevant_documents(message)
        source_urls, secondary_source_urls = self._get_source_urls(source_docs) if source_docs else ([], [])
        logger.info(f"Found {len(source_urls)} unique source URLs: {source_urls}")
        logger.info(f"Found {len(secondary_source_urls)} unique secondary source URLs: {secondary_source_urls}")

        # Prepare message with context if documents found
        if source_docs:
            context = self._format_context(source_docs)
            context = f"Contexte pouvant être utile pour répondre à la question:\n{context}"
            logger.info("Using document context for response")
        else:
            context = "Aucun document pertinent n'a été trouvé pour cette question: utiliser les connaissances générales mais prévenir l'utilisateur."
            logger.warning("No documents found, will use general knowledge with disclaimer")

        try:
            logger.info(f"Using model: {self.llm.model}")
            
            # Execute the chain with the properly formatted input
            response = self.chain_with_history.invoke(
                {"input": message, "context": context},
                config={"configurable": {"session_id": session_id}},
            )
            
            # response is a ColbertResponse instance
            logger.debug(f"Got answer: {response.answer}")
            logger.debug(f"Sources: {response.sources}")
            logger.debug(f"Secondary sources: {response.secondary_sources}")

            
            # Add disclaimer if no documents found
            if not source_docs:
                logger.info("No documents found, using general knowledge with disclaimer")
                response.answer = (
                    "Note: Je n'ai pas trouvé d'informations spécifiques dans ma base de données "
                    "pour répondre à votre question. Je vais donc répondre en me basant sur mes "
                    "connaissances générales. Veuillez noter que cette réponse n'est pas "
                    "nécessairement spécifique au contexte français ou aux services publics français.\n\n"
                ) + response.answer
                response.sources = ["https://www.service-public.fr"]
                response.secondary_sources = []
            
            # Format the response
            output = self._format_response(response)
            logger.info(f"Final response has {len(response.sources)} sources")
            logger.info(f"Final response has {len(response.secondary_sources)} secondary sources")
            logger.success(f"Response generated for message: {message}")
            logger.debug(f"Response preview: {output[:200]}...")
            
            # Store messages in history
            self.redis_service.store_message(
                session_id, {"role": "user", "content": message}
            )
            self.redis_service.store_message(
                session_id, {"role": "assistant", "content": output}
            )
            
            return output
            
        except Exception as e:
            logger.error(f"Error with model {self.llm.model}: {str(e)}")
            logger.exception("Full traceback:")
            return "Désolé, une erreur est survenue lors de la génération de la réponse."
