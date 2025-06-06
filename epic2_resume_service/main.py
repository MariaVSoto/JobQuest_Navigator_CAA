from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User, Resume, ResumeVersion
import os
from typing import List

DATABASE_URL = "sqlite:///./resume.db"
UPLOAD_DIR = "./epic2_resume_service/uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Management Service")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/resumes", response_model=dict)
def upload_resume(name: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 这里只做演示，实际应有用户认证
    user = db.query(User).first()
    if not user:
        user = User(username="demo", email="demo@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
    resume = Resume(name=name, user_id=user.id)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    version = ResumeVersion(resume_id=resume.id, file_path=file_location, comment="Initial upload")
    db.add(version)
    db.commit()
    db.refresh(version)
    return {"resume_id": resume.id, "version_id": version.id}

@app.get("/api/resumes", response_model=List[dict])
def list_resumes(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        return []
    resumes = db.query(Resume).filter(Resume.user_id == user.id).all()
    return [{"id": r.id, "name": r.name, "created_at": r.created_at} for r in resumes]

@app.get("/api/resumes/{resume_id}", response_model=dict)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    versions = db.query(ResumeVersion).filter(ResumeVersion.resume_id == resume.id).all()
    return {
        "id": resume.id,
        "name": resume.name,
        "created_at": resume.created_at,
        "versions": [{"id": v.id, "file_path": v.file_path, "created_at": v.created_at, "comment": v.comment} for v in versions]
    }

@app.post("/api/resumes/{resume_id}/versions", response_model=dict)
def upload_resume_version(resume_id: int, file: UploadFile = File(...), comment: str = Form(""), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    version = ResumeVersion(resume_id=resume.id, file_path=file_location, comment=comment)
    db.add(version)
    db.commit()
    db.refresh(version)
    return {"version_id": version.id}

@app.get("/api/resumes/{resume_id}/versions", response_model=List[dict])
def list_resume_versions(resume_id: int, db: Session = Depends(get_db)):
    versions = db.query(ResumeVersion).filter(ResumeVersion.resume_id == resume_id).all()
    return [{"id": v.id, "file_path": v.file_path, "created_at": v.created_at, "comment": v.comment} for v in versions]

@app.get("/api/files/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db)):
    version = db.query(ResumeVersion).filter(ResumeVersion.id == file_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(version.file_path, filename=os.path.basename(version.file_path))

@app.delete("/api/resumes/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    db.query(ResumeVersion).filter(ResumeVersion.resume_id == resume.id).delete()
    db.delete(resume)
    db.commit()
    return {"detail": "Resume deleted"}

@app.delete("/api/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    version = db.query(ResumeVersion).filter(ResumeVersion.id == file_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="File not found")
    if os.path.exists(version.file_path):
        os.remove(version.file_path)
    db.delete(version)
    db.commit()
    return {"detail": "File deleted"} 