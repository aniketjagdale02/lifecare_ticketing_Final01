from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import uuid
import os

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory
templates = Jinja2Templates(directory="templates")

TICKETS_FILE = "tickets.json"
USERS_FILE = "users.json"

# Load tickets from file
def load_tickets():
    if not os.path.exists(TICKETS_FILE):
        return []
    with open(TICKETS_FILE, "r") as f:
        return json.load(f)

# Save tickets to file
def save_tickets(tickets):
    with open(TICKETS_FILE, "w") as f:
        json.dump(tickets, f, indent=4)

# Load users
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

# Home route - redirect to login or dashboard
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    username = request.cookies.get("username")
    if username:
        return RedirectResponse("/dashboard")
    return RedirectResponse("/login")

# GET login page
@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# POST login
@app.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            response = RedirectResponse(url="/dashboard", status_code=302)
            response.set_cookie(key="username", value=username)
            return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

# Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/login")
    tickets = load_tickets()
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": username, "tickets": tickets})

# Create ticket
@app.get("/create", response_class=HTMLResponse)
def create_get(request: Request):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/login")
    return templates.TemplateResponse("create_ticket.html", {"request": request})

@app.post("/create")
def create_post(request: Request, subject: str = Form(...), description: str = Form(...)):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/login")

    tickets = load_tickets()
    new_ticket = {
        "id": str(uuid.uuid4()),
        "subject": subject,
        "description": description,
        "created_by": username
    }
    tickets.append(new_ticket)
    save_tickets(tickets)
    return RedirectResponse("/dashboard", status_code=302)

# Edit ticket
@app.get("/edit/{ticket_id}", response_class=HTMLResponse)
def edit_get(request: Request, ticket_id: str):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/login")

    tickets = load_tickets()
    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    if not ticket:
        return RedirectResponse("/dashboard")

    return templates.TemplateResponse("edit_ticket.html", {"request": request, "ticket": ticket})

@app.post("/edit/{ticket_id}")
def edit_post(request: Request, ticket_id: str, subject: str = Form(...), description: str = Form(...)):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/login")

    tickets = load_tickets()
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["subject"] = subject
            ticket["description"] = description
            break
    save_tickets(tickets)
    return RedirectResponse("/dashboard", status_code=302)

# Delete ticket
@app.get("/delete/{ticket_id}")
def delete_ticket(request: Request, ticket_id: str):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse("/login")

    tickets = load_tickets()
    tickets = [t for t in tickets if t["id"] != ticket_id]
    save_tickets(tickets)
    return RedirectResponse("/dashboard", status_code=302)

# Logout (POST method with cookie clearing)
@app.post("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("username")
    return response

# Forgot password
@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request, "phone": "8108271708"})
