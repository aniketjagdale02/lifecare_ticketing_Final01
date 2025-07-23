from fastapi import FastAPI, Request, Form, status, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import json
import os
from uuid import uuid4

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="verysecretkey")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

DATA_FILE = "tickets.json"

# Utility to load/save tickets
def load_tickets():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_tickets(tickets):
    with open(DATA_FILE, "w") as f:
        json.dump(tickets, f, indent=2)

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin123":
        request.session["user"] = username
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/dashboard")
def dashboard(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/", status_code=302)
    tickets = load_tickets()
    return templates.TemplateResponse("dashboard_ticket.html", {"request": request, "tickets": tickets})

@app.get("/create")
def create_ticket_page(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("create_ticket.html", {"request": request})

@app.post("/create")
def create_ticket(request: Request, customer_name: str = Form(...), email: str = Form(...),
                  contact: str = Form(...), issue_title: str = Form(...),
                  description: str = Form(...), status: str = Form(...),
                  assigned_to: str = Form(...), priority: str = Form(...), category: str = Form(...)):
    if "user" not in request.session:
        return RedirectResponse("/", status_code=302)
    tickets = load_tickets()
    new_ticket = {
        "id": str(uuid4()),
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
    save_tickets(tickets)
    return RedirectResponse("/dashboard", status_code=302)

@app.get("/edit/{ticket_id}")
def edit_ticket_page(request: Request, ticket_id: str):
    if "user" not in request.session:
        return RedirectResponse("/", status_code=302)
    tickets = load_tickets()
    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return templates.TemplateResponse("edit_ticket.html", {"request": request, "ticket": ticket})

@app.post("/edit/{ticket_id}")
def edit_ticket(request: Request, ticket_id: str, customer_name: str = Form(...), email: str = Form(...),
                contact: str = Form(...), issue_title: str = Form(...),
                description: str = Form(...), status: str = Form(...),
                assigned_to: str = Form(...), priority: str = Form(...), category: str = Form(...)):
    if "user" not in request.session:
        return RedirectResponse("/", status_code=302)
    tickets = load_tickets()
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
    save_tickets(tickets)
    return RedirectResponse("/dashboard", status_code=302)

@app.get("/delete/{ticket_id}")
def delete_ticket(request: Request, ticket_id: str):
    if "user" not in request.session:
        return RedirectResponse("/", status_code=302)
    tickets = load_tickets()
    tickets = [t for t in tickets if t["id"] != ticket_id]
    save_tickets(tickets)
    return RedirectResponse("/dashboard", status_code=302)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)
