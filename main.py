from fastapi import FastAPI, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import json, os

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Simulate login (hardcoded)
VALID_USERS = {
    "admin": "admin123",
    "aniket": "1234"
}

# Tickets stored in a JSON file
TICKET_FILE = "app/tickets.json"
if not os.path.exists(TICKET_FILE):
    with open(TICKET_FILE, "w") as f:
        json.dump([], f)

# -------------------- Routes ----------------------

@app.get("/")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if VALID_USERS.get(username) == password:
        response = RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="user", value=username)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/dashboard")
def dashboard(request: Request):
    user = request.cookies.get("user")
    if not user:
        return RedirectResponse("/", status_code=302)

    with open(TICKET_FILE, "r") as f:
        tickets = json.load(f)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "tickets": tickets})

@app.get("/create")
def create_ticket_form(request: Request):
    user = request.cookies.get("user")
    if not user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("create_ticket.html", {"request": request})

@app.post("/create")
def create_ticket(
    request: Request,
    customer_name: str = Form(...),
    email: str = Form(...),
    contact: str = Form(...),
    issue_title: str = Form(...),
    description: str = Form(...),
    status: str = Form(...),
    assigned_to: str = Form(...),
    priority: str = Form(...),
    category: str = Form(...)
):
    with open(TICKET_FILE, "r") as f:
        tickets = json.load(f)

    new_ticket = {
        "id": len(tickets) + 1,
        "customer_name": customer_name,
        "email": email,
        "contact": contact,
        "issue_title": issue_title,
        "description": description,
        "status": status,
        "assigned_to": assigned_to,
        "priority": priority,
        "category": category
    }
    tickets.append(new_ticket)
    with open(TICKET_FILE, "w") as f:
        json.dump(tickets, f, indent=4)

    return RedirectResponse("/dashboard", status_code=302)

@app.get("/edit/{ticket_id}")
def edit_ticket_form(request: Request, ticket_id: int):
    with open(TICKET_FILE, "r") as f:
        tickets = json.load(f)
    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    return templates.TemplateResponse("edit_ticket.html", {"request": request, "ticket": ticket})

@app.post("/edit/{ticket_id}")
def edit_ticket(
    request: Request,
    ticket_id: int,
    customer_name: str = Form(...),
    email: str = Form(...),
    contact: str = Form(...),
    issue_title: str = Form(...),
    description: str = Form(...),
    status: str = Form(...),
    assigned_to: str = Form(...),
    priority: str = Form(...),
    category: str = Form(...)
):
    with open(TICKET_FILE, "r") as f:
        tickets = json.load(f)

    for t in tickets:
        if t["id"] == ticket_id:
            t.update({
                "customer_name": customer_name,
                "email": email,
                "contact": contact,
                "issue_title": issue_title,
                "description": description,
                "status": status,
                "assigned_to": assigned_to,
                "priority": priority,
                "category": category
            })
            break

    with open(TICKET_FILE, "w") as f:
        json.dump(tickets, f, indent=4)

    return RedirectResponse("/dashboard", status_code=302)

@app.get("/delete/{ticket_id}")
def delete_ticket(ticket_id: int):
    with open(TICKET_FILE, "r") as f:
        tickets = json.load(f)
    tickets = [t for t in tickets if t["id"] != ticket_id]
    with open(TICKET_FILE, "w") as f:
        json.dump(tickets, f, indent=4)
    return RedirectResponse("/dashboard", status_code=302)

@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("user")
    return response
