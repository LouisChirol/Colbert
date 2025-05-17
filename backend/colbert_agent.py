import os
import time
from typing import List

from colbert_prompt import COLBERT_PROMPT, OUTPUT_PROMPT, TOOLS_PROMPT
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_mistralai import ChatMistralAI
from loguru import logger
from pydantic import BaseModel, Field
from redis_service import RedisService
from search_tool import WebsiteSearchTool

load_dotenv()


MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is not set")

MISTRAL_MODELS = ["mistral-large", "mistral-medium", "mistral-small"]


class ColbertResponse(BaseModel):
    answer: str = Field(description="The answer to the user's question")
    sources: List[str] = Field(
        description="The sources used to answer the user's question, should be a list of urls"
    )


class ColbertAgent:
    def __init__(self):
        # Initialize Redis service
        self.redis_service = RedisService()

        # Initialize search tool
        self.search_tool = WebsiteSearchTool()
        self.tools = [self.search_tool.get_tool()]

        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", COLBERT_PROMPT),
                ("system", TOOLS_PROMPT),
                ("system", OUTPUT_PROMPT),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
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

        # Create the agent with tools
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )

        # Create the agent executor with proper configuration
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

        # Chain with history
        self.chain_with_history = RunnableWithMessageHistory(
            self.agent_executor,
            self.get_redis_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def get_redis_history(self, session_id: str):
        history = self.redis_service.get_history(session_id)
        logger.debug(f"History: {history}")
        return history

    def _format_response(self, response: ColbertResponse) -> str:
        """Format the response with sources using markdown."""
        # Format the answer with proper spacing and line breaks
        formatted_answer = response.answer.strip()
        
        # Format sources as markdown links with prefix
        sources_text = "\n\nSources:\n"
        for source in response.sources:
            sources_text += f"- [{source}]({source})\n"
            
        return formatted_answer + sources_text

    def ask_colbert(self, message: str, session_id: str) -> str:
        for model in MISTRAL_MODELS:
            try:
                logger.info(f"Attempting to use model: {model}")
                self._initialize_llm(model)
                
                response = self.chain_with_history.invoke(
                    {"input": message, "session_id": session_id},
                    config={"configurable": {"session_id": session_id}},
                )

                # Extract and parse the output
                if isinstance(response, dict) and "output" in response:
                    try:
                        structured_output = ColbertResponse.model_validate_json(response["output"])
                        output = self._format_response(structured_output)
                    except Exception as e:
                        logger.warning(f"Failed to parse structured output: {str(e)}")
                        output = str(response["output"])
                else:
                    output = str(response)

                logger.success(f"Response generated for message: {message}")
                logger.success(f"Response: {output}")

                self.redis_service.store_message(
                    session_id, {"role": "user", "content": message}
                )
                self.redis_service.store_message(
                    session_id, {"role": "assistant", "content": output}
                )
                return output

            except Exception as e:
                logger.warning(f"Error with model {model}: {str(e)}; waiting 3s")
                time.sleep(3)
                if model == MISTRAL_MODELS[-1]:  # If this was the last model
                    logger.error(f"All models failed. Last error: {str(e)}")
                    return "Désolé, une erreur est survenue. Veuillez réessayer."
                continue  # Try the next model
