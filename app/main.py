from fastapi import FastAPI, Body, Response, status, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine,SessionLocal

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None
    id: Optional[int] = None

while True:
    try:
        conn = psycopg2.connect(host="localhost", port=5434, database="fastapi", user="postgres", password="admin", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connected successfully")
        break
    except Exception as error:
        print("Error connecting database")
        print("error= ",error)
        time.sleep(2)

my_posts = [{"title":"A","content":"a","published":False,"id":1},{"title":"B","content":"b","published":False,"id":2}]

def find_post(id):
    for post in my_posts:
        if post['id']==id:
           return post
        
def find_index_post(id):
    for i, post in enumerate(my_posts):
        if post['id'] == id:
            return i

@app.get("/")
async def get_hello():
    return {"Hello: ": "Nepal dfasdadf dd"}
    
@app.get("/sqlalchemy")
async def test_db(db: Session = Depends(get_db)):
    return {"status ": "success"}
    
@app.get("/allposts")
async def get_posts():
    cursor.execute("""SELECT * FROM posts """)
    post = cursor.fetchall()
    return {"All Posts":post}

@app.post("/posts",status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    # print("The details are: ",post)
    # post_dict = post.dict() 
    # post_dict['id']= randrange(0,100000)
    # my_posts.append(post_dict)
    # return {"message":f"{"title":new_post.title}, {"content":new_post.content}"}
    # print(post)
    cursor.execute("""INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING
                    * """,
                             (post.title,post.content,post.published))
    conn.commit()
    new_post = cursor.fetchone()
    return {"data":new_post}

@app.get("/posts/{id}")
async def get_post(id: int, response=Response):
    cursor.execute(""" SELECT * FROM posts WHERE id = %s """,(str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} is not found") 
    return {"Your post":post}

@app.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id:int):
    # print("The id is: ",id)
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """,(str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    # index = find_index_post(id)
    if delete_post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with this {id} is not found")
    # my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/updatepost/{id}")
async def update_post(id:int,post:Post):
    # print("The post details are: ",post)
    cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id = %s RETURNING * """,(post.title,post.content,post.published,str(id),))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with this {id} is not found")
    return {"data: ", updated_post}