from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from transformers import AutoTokenizer

# Define max tokens allowed for history
MAX_TOKENS = 1024

def _message_to_text(message: BaseMessage) -> str:
    if isinstance(message, HumanMessage):
        role = "user"
    elif isinstance(message, AIMessage):
        role = "assistant"
    elif isinstance(message, SystemMessage):
        role = "system"
    else:
        role = "unknown"
    return f"{role}: {message.content}"

class MyLLM:
    llm = None
    tokenizer = None
    workflow = None
    memory = None
    app = None

    def __init__(self):
        self.llm = ChatOpenAI(
            model="/app/local_model",
            openai_api_key="token-abc123",
            openai_api_base="http://127.0.0.1:8080/v1",
            max_tokens=1024,
            temperature=0,
        )

        self._init_workflow()
        self._init_tokenizer()

    def _init_tokenizer(self):
        self.tokenizer = AutoTokenizer.from_pretrained("/app/local_model")

    def _trim_message(self, messages):
        trimmed = []
        total_tokens = 0

        for message in reversed(messages):
            text = _message_to_text(message)
            num_tokens = len(self.tokenizer.encode(text, add_special_tokens=False))
            if total_tokens + num_tokens > MAX_TOKENS:
                break
            trimmed.insert(0, message)
            total_tokens += num_tokens

        return trimmed

    def _init_workflow(self):
        self.workflow = StateGraph(state_schema=MessagesState)
        self.workflow.add_node("model", self._call_model)
        self.workflow.add_edge(START, "model")

        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)

    def _call_model(self, state: MessagesState):
        trimmed_messages = self._trim_message(state["messages"])
        response = self.llm.invoke(trimmed_messages)
        return {"messages": response}

    def chat(self, message: str, thread_id: str) -> str:
        if not self.llm:
            raise Exception("Local LLM not initialized.")
        
        try:
            output = self.app.invoke(
                {
                    "messages": [HumanMessage(content=message)]
                },
                config={
                    "configurable": {
                        "thread_id": thread_id
                    }
                }
            )

            return output["messages"][-1].content

        except Exception as e:
            raise Exception(str(e))
