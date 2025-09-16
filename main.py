from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crewai import Agent, Task, Crew
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Duecey Story Generator", version="1.0.0")

class StoryRequest(BaseModel):
    theme: str = "adventure"
    duration_seconds: int = 36
    number_of_scenes: int = 7

class Scene(BaseModel):
    scene_number: int
    description: str
    duration_seconds: float
    location: str = "various"
    action: str = "adventure" 
    mood: str = "cheerful"

class StoryResponse(BaseModel):
    title: str
    total_duration: int
    scenes: list
    overall_mood: str = "cheerful"

def create_story_agent():
    return Agent(
        role='Duecey Adventure Story Creator',
        goal='Create engaging, short-form stories for Duecey the Shih Tzu puppy',
        backstory='''You are a specialist in creating viral short-form content featuring Duecey, 
        a lovable Shih Tzu puppy. You understand visual storytelling and what makes content shareable. 
        You always include food elements and ensure Duecey has satisfying, relatable adventures.''',
        verbose=True,
        allow_delegation=False
    )

@app.post("/generate-story")
async def generate_story(request: StoryRequest):
    try:
        story_agent = create_story_agent()
        
        story_task = Task(
            description=f"""Create a {request.duration_seconds}-second story for Duecey the Shih Tzu puppy 
            with exactly {request.number_of_scenes} scenes. Theme: {request.theme}.
            
            Duecey Character Profile:
            - Adorable Shih Tzu puppy with fluffy white and brown fur
            - Wears stylish sunglasses when driving/being cool  
            - Loves food adventures and relaxation
            - Has sophisticated taste (Starbucks coffee, deli subs)
            
            Please respond with:
            Title: [Creative title]
            Scene 1: [Detailed visual description]
            Scene 2: [Detailed visual description] 
            Scene 3: [Detailed visual description]
            ... etc
            
            Focus on visual actions that animate well.
            """,
            agent=story_agent,
            expected_output="A structured story with title and scene descriptions"
        )
        
        crew = Crew(
            agents=[story_agent],
            tasks=[story_task],
            verbose=True
        )
        
        result = crew.kickoff()
        story_text = str(result)
        lines = story_text.split('\n')
        
        title = f"Duecey's {request.theme} Adventure"
        scenes = []
        scene_duration = request.duration_seconds / request.number_of_scenes
        
        # Extract title if present
        for line in lines:
            if "Title:" in line:
                title = line.replace("Title:", "").strip()
                break
        
        # Extract scenes
        scene_count = 0
        for line in lines:
            if line.strip().startswith("Scene") and scene_count < request.number_of_scenes:
                scene_count += 1
                scenes.append({
                    "scene_number": scene_count,
                    "description": line.strip(),
                    "duration_seconds": scene_duration,
                    "location": "auto-detected",
                    "action": "adventure",
                    "mood": "cheerful"
                })
        
        return {
            "title": title,
            "total_duration": request.duration_seconds,
            "scenes": scenes,
            "overall_mood": "cheerful"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "duecey-story-generator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
