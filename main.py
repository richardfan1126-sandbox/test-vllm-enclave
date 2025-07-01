if __name__ == "__main__":
    from langchain_community.llms import VLLM

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

    # print(llm("What is the capital of France ?"))


    from langchain.chains import LLMChain
    from langchain_core.prompts import PromptTemplate

    template = """Question: {question}

    Answer: Let's think step by step."""
    prompt = PromptTemplate.from_template(template)

    llm_chain = LLMChain(prompt=prompt, llm=llm)

    question = "Can you write me a poem?"

    print(llm_chain.invoke(question))
