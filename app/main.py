from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
from .hashing import Hash
from .schema import Configuration, DeviceInfo

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()




@app.post('/device/info')
def save_device_info(info: DeviceInfo, db=Depends(db)):
    object_in_db = crud.get_device_info(db, info.token)
    if object_in_db:
        raise HTTPException(400, detail= crud.error_message('This device info already exists'))
    return crud.save_device_info(db,info)

@app.get('/device/info/{token}')
def get_device_info(token: str, db=Depends(db)):
    info = crud.get_device_info(db,token)
    if info:
        return info
    else:
        raise HTTPException(404, crud.error_message('No device found for token {}'.format(token)))

@app.get('/device/info')
def get_all_device_info(db=Depends(db)):
    return crud.get_device_info(db)

@app.post('/configuration')
def save_configuration(config: Configuration, db=Depends(db)):
    # always maintain one config
    crud.delete_nudges_configuration(db)
    return crud.save_nudges_configuration(db, config)

@app.get('/configuration')
def get_configuration(db=Depends(db)):
    config = crud.get_nudges_configuration(db)
    if config:
        return config
    else:
        raise HTTPException(404, crud.error_message('No configuration set'))
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    

@app.post('/user',response_model=schemas.ShowUser,tags=['Users'])
def create_user(request:schemas.User, db:Session = Depends(get_db)):
    0
    new_user = models.User(name=request.name,email=request.email,password=Hash.bcrypt(request.password))
   
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user




@app.get('/user/{id}',status_code=status.HTTP_200_OK,response_model=schemas.ShowUser,tags=['Users'])
def get_user(id:int,db:Session = Depends(get_db)):
    User = db.query(models.User).filter(models.User.id==id).first()
    if not User:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user with the id {id} not available")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return{'details':f'blog with the id {id} not available'}
    return User

    
@app.post('/blog',status_code=status.HTTP_201_CREATED,tags=['Blogs'])
def create(blog: schemas.Blog ,db = Depends(get_db)):
    new_blog = models.Blog(title=blog.title,body =blog.body,user_id =blog.user_id) 
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.get('/blog',response_model=List[schemas.showBlog],tags=['Blogs'])
def all(db = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs




@app.get('/blog/{id}',status_code=status.HTTP_200_OK,response_model=schemas.showBlog,tags=['Blogs'])
def show(id,response : Response ,db = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id==id).first()
    if not blog:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"blog with the id {id} not available")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return{'details':f'blog with the id {id} not available'}
    return blog


@app.delete('/blog/{id}',status_code=status.HTTP_204_NO_CONTENT,tags=['Blogs'])
def destroy(id,db = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id==id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'blog with the id {id} not found')
    
    blog.delete(synchronize_session=False) 
    db.commit()
    return 'the blog is deleted from the database'


@app.put('/blog/{id}',status_code=status.HTTP_202_ACCEPTED,tags=['Blogs'])
def update(id,request: schemas.Blog , db = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'blog with the id {id} not found')
    blog.update({'title': request.title, 'body': request.body})
    db.commit()
    return 'updated'
    
    
