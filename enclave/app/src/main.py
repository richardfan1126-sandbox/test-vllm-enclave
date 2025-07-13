from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from attestation import get_attestation_doc
from encryption import Encryption
from llm import MyLLM

app = FastAPI()

# Global state
encryption = Encryption()
my_llm = None

class GetAttestationReq(BaseModel):
    nonce: str

class GetAttestationResponse(BaseModel):
    attestation_doc: str

class ConversationRequest(BaseModel):
    public_key: str
    encrypted_payload: str
    encrypted_nonce: str

class ConversationResponse(BaseModel):
    attestation_doc: str
    encrypted_response: str

@app.get("/health-check")
def health_check():
    return ""

@app.post("/get-attestation", response_model=GetAttestationResponse)
def get_attestation(req: GetAttestationReq):
    nonce = req.nonce.encode()
    public_key = encryption.get_pub_key_bytes()
    user_data = None
    
    attestation_doc = get_attestation_doc(public_key, user_data, nonce)
    if not attestation_doc:
        raise HTTPException(status_code=500, detail="Cannot get attestation document")

    return GetAttestationResponse(attestation_doc=attestation_doc)

@app.post("/chat", response_model=ConversationResponse)
def chat(req: ConversationRequest):
    if not my_llm:
        raise HTTPException(status_code=500, detail="Local LLM not initialized.")

    client_pub_key_b64 = req.public_key
    session_key = encryption.get_session_key(client_pub_key_b64)

    encrypted_payload = req.encrypted_payload
    payload = Encryption.decrypt(encrypted_payload, session_key)

    try:
        llm_response = my_llm.chat(payload, "123")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    encrypted_response = Encryption.encrypt(llm_response, session_key)

    encrypted_nonce = req.encrypted_nonce
    nonce = Encryption.decrypt(encrypted_nonce, session_key).encode()

    public_key = None
    user_data = Encryption.get_hash(llm_response)

    attestation_doc = get_attestation_doc(public_key, user_data, nonce)
    if not attestation_doc:
        raise HTTPException(status_code=500, detail="Cannot get attestation document")

    return ConversationResponse(
        attestation_doc = attestation_doc,
        encrypted_response = encrypted_response
    )

if __name__ == "__main__":
    my_llm = MyLLM()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="trace")
