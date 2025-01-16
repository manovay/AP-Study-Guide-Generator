from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models.generate_guide import generate_study_guide

app = FastAPI()

# Input model
class Prompt(BaseModel):
    user_prompt: str

@app.post("/generate-guide")
async def generate_guide(prompt: Prompt):
    try:
        study_guide = generate_study_guide(prompt.user_prompt)
        return {"study_guide": study_guide}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))