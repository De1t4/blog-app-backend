from fastapi import FastAPI
from routers import posts, users, comments, like, followers
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
from dotenv import load_dotenv
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

cloudinary.config( 
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(comments.router)
app.include_router(like.router)
app.include_router(followers.router)
