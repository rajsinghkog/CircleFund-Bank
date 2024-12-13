from fastapi import FastAPI, Depends, Request, Form, status
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
from owndatabase import SessionLocal, engine
import model2 
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

def apply_interest():
    with SessionLocal() as db:
        accounts = db.query(model2.bank).all()
        for acc in accounts:
            daily_rate = acc.interest_rate/365
            interest = acc.amount * daily_rate
            acc.amount += interest
            acc.last_interest_applied = datetime.now()
        db.commit()
    print("Interest applied to all accounts.")

scheduler = BackgroundScheduler()


scheduler.add_job(apply_interest, 'interval', seconds=60)
scheduler.start()

model2.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

@app.get("/")
async def home(req: Request, db: Session = Depends(get_db)):
    dlist = db.query(model2.bank).all()  
    return templates.TemplateResponse("trial.html", { "request": req, "dlist": dlist })


@app.post("/add")
def add(req: Request, title: str = Form(...), number: str = Form(...), db: Session = Depends(get_db)):

    new_acc = model2.bank(name=title, amount=number)  
    db.add(new_acc)
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/withdrawl100/{acc_id}")
def add(req: Request, acc_id: int, db: Session = Depends(get_db)):
    acc = db.query(model2.bank).filter(model2.bank.id == acc_id).first()
    acc.amount=acc.amount-100
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)
@app.get("/withdrawl500/{acc_id}{deposit}")
def add(req: Request, acc_id: int, db: Session = Depends(get_db)):
    acc = db.query(model2.bank).filter(model2.bank.id == acc_id).first()
    acc.amount=acc.amount-500
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/update100/{acc_id}")
def add(req: Request, acc_id: int, db: Session = Depends(get_db)):
    acc = db.query(model2.bank).filter(model2.bank.id == acc_id).first()
    acc.amount=acc.amount+100
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/update500/{acc_id}")
def add(req: Request, acc_id: int, db: Session = Depends(get_db)):
    acc = db.query(model2.bank).filter(model2.bank.id == acc_id).first()
    acc.amount=acc.amount+500
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/delete/{acc_id}")
def add(req: Request, acc_id: int, db: Session = Depends(get_db)):
    acc= db.query(model2.bank).filter(model2.bank.id == acc_id).first()
    db.delete(acc)
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)