from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import json
import os
import uuid

app = FastAPI()

# Add SessionMiddleware for session management
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# Mount static folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Files for storing tickets and users
TICKET_FILE = "tickets.json"
USER_FILE = "users.json"

# Ensure JSON files exist
if not os.path.exists(TICKET_FILE):
    with open(TICKET_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump([{"username": "admin", "password": "admin123"}], f)


@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/login")


@app.route("/login", methods=["GET", "POST"])
async def login(request: Request):
    if request.method == "GET":
        return templates.TemplateResponse("login.html", {"request": request})

    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    with open(USER_FILE, "r") as f:
        users = json.load(f)

    user = next((u for u in users if u["username"] == username and u["password"] == password), None)

    if user:
        request.session["user"] = user["username"]
        return RedirectResponse(url="/dashboard", status_code=302)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")


@app.get("/dashboard")
async def dashboard(request: Request):
    if "user" not in request.session:
        return RedirectResponse(url="/login")
    with open(TICKET_FILE, "r") as f:
        tickets = json.load(f)
    return templates.TemplateResponse("dashboard.html", {"request": request, "tickets": tickets})


@app.get("/create")
async def create_get(request: Request):
    if "user" not in request.session:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("create_ticket.html", {"request": request})


@app.post("/create")
async def create_post(request: Request, customer: str = Form(...), issue: str = Form(...)):
    if "user" not in request.session:
        return RedirectResponse(url="/login")
    with open(TICKET_FILE, "r") as f:
        tickets = json.load(f)
    new_ticket = {
        "id": str(uuid.uuid4()),
        "customer": customer,
        "issue": issue
    }
    tickets.append(new_ticket)
    with open(TICKET_FILE, "w") as f:
        json.dump(tickets, f, indent=4)
    return RedirectResponse(url="/dashboard", status_code=302)


@app.get("/edit/{ticket_id}")
async def edit_get(request: Request, ticket_id: str):
    if "user" not in request.session:
        return RedirectResponse(url="/login")
    with open(TICKET_FILE, "r") as f:
        tickets = json.load(f)
    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    return templates.TemplateResponse("edit_ticket.html", {"request": request, "ticket": ticket})


@app.post("/edit/{ticket_id}")
async def edit_post(request: Request, ticket_id: str, customer: str = Form(...), issue: str = Form(...)):
    if "user" not in request.session:
        return RedirectResponse(url="/login")
    with open(TICKET_FILE, "r") as f:
        tickets = json.load(f)
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["customer"] = customer
            ticket["issue"] = issue
            break
    with open(TICKET_FILE, "w") as f:
        json.dump(tickets, f, indent=4)
    return RedirectResponse(url="/dashboard", status_code=302)


@app.get("/delete/{ticket_id}")
async def delete_ticket(request: Request, ticket_id: str):
    if "user" not in request.session:
        return RedirectResponse(url="/login")
    with open(TICKET_FILE, "r") as f:
        tickets = json.load(f)
    tickets = [t for t in tickets if t["id"] != ticket_id]
    with open(TICKET_FILE, "w") as f:
        json.dump(tickets, f, indent=4)
    return RedirectResponse(url="/dashboard", status_code=302)
