from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from models.generate_guide import generate_study_guide  # Relative import
from routes.user_routes import router as user_router  # Relative import
from db import close_connection
from datetime import datetime
from bson import ObjectId
from db import users_collection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions (if needed)
    yield
    # Shutdown actions
    await close_connection()

# Initialize FastAPI with lifespan
app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin. Replace "*" with specific origins for better security.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, etc.).
    allow_headers=["*"],  # Allows all headers.
)

# Input model
class Prompt(BaseModel):
    user_prompt: str


# Include user routes
app.include_router(user_router, prefix="/api")

@app.on_event("shutdown")
async def shutdown():
    await close_connection()

@app.get("/")
async def root():
    return {"message": "Welcome to TooturAI Backend"}

# @app.post("/generate-guide")
# async def generate_guide(prompt: Prompt):
#     try:
#         study_guide = generate_study_guide(prompt.user_prompt)
#         return {"study_guide": study_guide}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
class StudyGuideRequest(BaseModel):
    email: str  # Ensure email is required
    user_prompt: str
    study_guide_id: str = None  # Optional for follow-ups


@app.post("/generate-guide")
async def generate_guide(request: StudyGuideRequest):
    try:
        # Extract data from the request body
        email = request.email
        user_prompt = request.user_prompt
        study_guide_id = request.study_guide_id

        # Validate email
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        # Generate AI response
        new_response = generate_study_guide(user_prompt)

        # If modifying an existing study guide, append to it
        if study_guide_id:
            guide = await users_collection.find_one(
                {"email": email, "study_guides._id": study_guide_id}
            )

            if not guide:
                raise HTTPException(status_code=404, detail="Study guide not found")

            # Append conversation history
            await users_collection.update_one(
                {"email": email, "study_guides._id": study_guide_id},
                {"$push": {"study_guides.$.conversation": {"user_prompt": user_prompt, "response": new_response}}}
            )

            return {"message": "Response added to existing study guide", "response": new_response}

        # Create a new study guide session
        new_study_guide = {
            "_id": str(ObjectId()),  
            "title": user_prompt[:50],  # Use first few words as title
            "conversation": [{"user_prompt": user_prompt, "response": new_response}],
            "created_at": datetime.utcnow()
        }

        # Store new study guide in database
        await users_collection.update_one(
            {"email": email},
            {"$push": {"study_guides": new_study_guide}},
            upsert=True
        )

        return {"message": "New study guide created", "study_guide": new_study_guide}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))