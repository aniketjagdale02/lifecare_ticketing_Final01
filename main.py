from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import json
import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="lifecare_session_2025")
# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates path
templates = Jinja2Templates(directory="app/templates")

# File paths
TICKETS_FILE = "app/tickets.json"
USERS_FILE = "app/users.json"

# Utility Functions
def load_tickets():
    if not os.path.exists(TICKETS_FILE):
        return []
    with open(TICKETS_FILE, "r") as f:
        return json.load(f)

def save_tickets(tickets):
    with open(TICKETS_FILE, "w") as f:
        json.dump(tickets, f, indent=2)

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def authenticate_user(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return True
    return False

# Routes
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if authenticate_user(username, password):
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="username", value=username)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse(url="/", status_code=302)
    tickets = load_tickets()
    return templates.TemplateResponse("dashboard_ticket.html", {"request": request, "tickets": tickets, "username": username})

@app.get("/create", response_class=HTMLResponse)
def create_ticket_form(request: Request):
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
    tickets = load_tickets()
    ticket_id = max([ticket["id"] for ticket in tickets], default=0) + 1
    new_ticket = {
        "id": ticket_id,
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
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/edit/{ticket_id}", response_class=HTMLResponse)
def edit_ticket(request: Request, ticket_id: int):
    tickets = load_tickets()
    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    if not ticket:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("edit_ticket.html", {"request": request, "ticket": ticket})

@app.post("/edit/{ticket_id}")
def update_ticket(
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
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/delete/{ticket_id}")
def delete_ticket(ticket_id: int):
    tickets = load_tickets()
    tickets = [t for t in tickets if t["id"] != ticket_id]
    save_tickets(tickets)
    return RedirectResponse(url="/dashboard", status_code=302)

from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import json
import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="lifecare_session_2025")
# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates path
templates = Jinja2Templates(directory="app/templates")

# File paths
TICKETS_FILE = "app/tickets.json"
USERS_FILE = "app/users.json"

# Utility Functions
def load_tickets():
    if not os.path.exists(TICKETS_FILE):
        return []
    with open(TICKETS_FILE, "r") as f:
        return json.load(f)

def save_tickets(tickets):
    with open(TICKETS_FILE, "w") as f:
        json.dump(tickets, f, indent=2)

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def authenticate_user(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return True
    return False

# Routes
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if authenticate_user(username, password):
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="username", value=username)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse(url="/", status_code=302)
    tickets = load_tickets()
    return templates.TemplateResponse("dashboard_ticket.html", {"request": request, "tickets": tickets, "username": username})

@app.get("/create", response_class=HTMLResponse)
def create_ticket_form(request: Request):
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
    tickets = load_tickets()
    ticket_id = max([ticket["id"] for ticket in tickets], default=0) + 1
    new_ticket = {
        "id": ticket_id,
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
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/edit/{ticket_id}", response_class=HTMLResponse)
def edit_ticket(request: Request, ticket_id: int):
    tickets = load_tickets()
    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    if not ticket:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("edit_ticket.html", {"request": request, "ticket": ticket})

@app.post("/edit/{ticket_id}")
def update_ticket(
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
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/delete/{ticket_id}")
def delete_ticket(ticket_id: int):
    tickets = load_tickets()
    tickets = [t for t in tickets if t["id"] != ticket_id]
    save_tickets(tickets)
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()  # Clear the session data
    return RedirectResponse(url="/login", status_code=302)
