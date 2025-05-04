import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from loguru import logger
from dotenv import load_dotenv
from redis_service import RedisService
from colbert_prompt import COLBERT_PROMPT

load_dotenv()


MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is not set")

MISTRAL_MODEL = "mistral-medium"


class ColbertAgent:
    def __init__(self):
        # Initialize Redis service
        self.redis_service = RedisService()
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", COLBERT_PROMPT),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )
        # Initialize the LLM
        self.llm = ChatMistralAI(
            model=MISTRAL_MODEL,
            temperature=0.7,  # Slightly increased for more natural responses
            max_retries=2,
            api_key=MISTRAL_API_KEY,
        )
        # Create the chain
        self.chain = self.prompt | self.llm | StrOutputParser()
        # Chain with history
        self.chain_with_history = RunnableWithMessageHistory(
            self.chain,
            self.get_redis_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def get_redis_history(self, session_id: str):
        history = self.redis_service.get_history(session_id)
        logger.info(f"History: {history}")
        return history

    def ask_colbert(self, message: str, session_id: str) -> str:
        try:
            response = self.chain_with_history.invoke(
                {"input": message, "session_id": session_id},
                config={"configurable": {"session_id": session_id}},
            )
            logger.success(f"Response generated for message: {message}")

            self.redis_service.store_message(
                session_id, {"role": "user", "content": message}
            )
            self.redis_service.store_message(
                session_id, {"role": "assistant", "content": response}
            )
            return response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "Désolé, une erreur est survenue. Veuillez réessayer."
