from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
import sqlite3
import os

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Utility to get DB connection
def get_db_connection():
    conn = sqlite3.connect("ticketing.db")
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------------
# Login Page
# -------------------------------

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    # Dummy check - replace with real user validation
    if username == "admin" and password == "admin":
        request.session["user"] = username
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


# -------------------------------
# Logout
# -------------------------------

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


# -------------------------------
# Dashboard (Auth-protected)
# -------------------------------

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=302)
    
    conn = get_db_connection()
    tickets = conn.execute("SELECT * FROM tickets").fetchall()
    conn.close()
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "tickets": tickets})


# -------------------------------
# Create Ticket
# -------------------------------

@app.get("/create", response_class=HTMLResponse)
def create_ticket_get(request: Request):
    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("create_ticket.html", {"request": request})


@app.post("/create")
def create_ticket_post(request: Request, title: str = Form(...), description: str = Form(...)):
    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=302)
    
    conn = get_db_connection()
    conn.execute("INSERT INTO tickets (title, description) VALUES (?, ?)", (title, description))
    conn.commit()
    conn.close()
    
    return RedirectResponse(url="/dashboard", status_code=302)


# -------------------------------
# Edit Ticket
# -------------------------------

@app.get("/edit/{ticket_id}", response_class=HTMLResponse)
def edit_ticket_get(request: Request, ticket_id: int):
    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=302)
    
    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    conn.close()
    
    if not ticket:
        return HTMLResponse(content="Ticket not found", status_code=404)
    
    return templates.TemplateResponse("edit_ticket.html", {"request": request, "ticket": ticket})


@app.post("/edit/{ticket_id}")
def edit_ticket_post(request: Request, ticket_id: int, title: str = Form(...), description: str = Form(...)):
    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=302)
    
    conn = get_db_connection()
    conn.execute("UPDATE tickets SET title = ?, description = ? WHERE id = ?", (title, description, ticket_id))
    conn.commit()
    conn.close()
    
    return RedirectResponse(url="/dashboard", status_code=302)


# -------------------------------
# Home Redirect
# -------------------------------

@app.get("/")
def root():
    return RedirectResponse(url="/login", status_code=302)
