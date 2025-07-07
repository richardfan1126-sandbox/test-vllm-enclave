from langchain_community.llms import VLLM
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

class MyLLM:
    llm = None

    def __init__(self):
        # Initialize vLLM model via LangChain
        self.llm = VLLM(model="/app/local_model",
            trust_remote_code=True,  # mandatory for hf models
            max_new_tokens=128,
            top_k=10,
            top_p=0.95,
            temperature=0.8,
            vllm_kwargs={
                "swap_space": 2,
                "device": "cpu",
            },
            # tensor_parallel_size=... # for distributed inference
        )

    def chat(self, request: str) -> str:
        if not self.llm:
            raise Exception("Local LLM not initialized.")
        
        try:
            template = """Question: {question}

            Answer: Let's think step by step."""
            prompt = PromptTemplate.from_template(template)
            llm_chain = LLMChain(prompt=prompt, llm=self.llm)
            response = llm_chain.invoke(request)
            return response["text"]

        except Exception as e:
            raise Exception(str(e))
