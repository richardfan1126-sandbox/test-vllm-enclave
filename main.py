from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.llms import VLLM
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
import uvicorn

# Define request and response models
class ConversationRequest(BaseModel):
    user_input: str

class ConversationResponse(BaseModel):
    response: dict

app = FastAPI()
llm = None

@app.post("/chat", response_model=ConversationResponse)
def chat(request: ConversationRequest):
    global llm

    if not llm:
        raise HTTPException(status_code=500, detail="Local LLM not initialized.")
    
    try:
        template = """Question: {question}

        Answer: Let's think step by step."""
        prompt = PromptTemplate.from_template(template)
        llm_chain = LLMChain(prompt=prompt, llm=llm)
        response = llm_chain.invoke(request.user_input)
        return ConversationResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    global llm

    # Initialize vLLM model via LangChain
    llm = VLLM(model="/workspace/local_model",
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

    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
