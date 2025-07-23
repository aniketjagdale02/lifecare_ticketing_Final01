from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_302_FOUND
import models
import database
import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")  # Replace with a real secret in production

app.mount("/static", StaticFiles(directory=os.path.join("app", "static")), name="static")

templates = Jinja2Templates(directory=os.path.join("app", "templates"))


# Dummy credentials
USER_CREDENTIALS = {
    "admin": "admin123"
}

@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        request.session["user"] = username
        return RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)

def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    return user

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not request.session.get("user"):
        return RedirectResponse(url="/login")
    db = database.SessionLocal()
    tickets = db.query(models.Ticket).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "tickets": tickets})

@app.get("/create", response_class=HTMLResponse)
async def create_ticket_form(request: Request):
    if not request.session.get("user"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("create_ticket.html", {"request": request})

@app.post("/create")
async def create_ticket(request: Request,
                        title: str = Form(...),
                        description: str = Form(...),
                        status: str = Form(...)):
    if not request.session.get("user"):
        return RedirectResponse(url="/login")
    db = database.SessionLocal()
    new_ticket = models.Ticket(title=title, description=description, status=status)
    db.add(new_ticket)
    db.commit()
    return RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)

@app.get("/edit/{ticket_id}", response_class=HTMLResponse)
async def edit_ticket_form(request: Request, ticket_id: int):
    if not request.session.get("user"):
        return RedirectResponse(url="/login")
    db = database.SessionLocal()
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    return templates.TemplateResponse("edit_ticket.html", {"request": request, "ticket": ticket})

@app.post("/edit/{ticket_id}")
async def edit_ticket(request: Request, ticket_id: int,
                      title: str = Form(...),
                      description: str = Form(...),
                      status: str = Form(...)):
    if not request.session.get("user"):
        return RedirectResponse(url="/login")
    db = database.SessionLocal()
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    ticket.title = title
    ticket.description = description
    ticket.status = status
    db.commit()
    return RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)

@app.get("/delete/{ticket_id}")
async def delete_ticket(request: Request, ticket_id: int):
    if not request.session.get("user"):
        return RedirectResponse(url="/login")
    db = database.SessionLocal()
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    db.delete(ticket)
    db.commit()
    return RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)
