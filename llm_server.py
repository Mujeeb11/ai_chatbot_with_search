from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

app = FastAPI()

# Load GPT2
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")
model.eval()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: list[Message]
    stream: bool = True

def format_prompt(messages):
    return "\n".join([f"{m.role}: {m.content}" for m in messages]) + "\nassistant:"

async def generate_stream(prompt):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output_ids = input_ids
    for _ in range(50):  # stream 50 tokens
        with torch.no_grad():
            logits = model(output_ids)[0][:, -1, :]
            next_token = torch.argmax(logits, dim=-1)
            output_ids = torch.cat([output_ids, next_token.unsqueeze(0)], dim=1)
            new_token = tokenizer.decode(next_token)
            yield f'data: {{"choices":[{{"delta":{{"content":"{new_token}"}}}}]}}\n\n'
            if new_token in ["", ".", "\n"]: break

@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    prompt = format_prompt(req.messages)
    if req.stream:
        return StreamingResponse(generate_stream(prompt), media_type="text/event-stream")
    else:
        with torch.no_grad():
            input_ids = tokenizer.encode(prompt, return_tensors="pt")
            output = model.generate(input_ids, max_length=150)
            output_text = tokenizer.decode(output[0])
            return {
                "choices": [{"message": {"role": "assistant", "content": output_text.split("assistant:")[-1]}}]
            }