import asyncio
import json
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request, Header
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import auth as Auth
import database as db
from agents import get_agents, save_agent, WorkflowState, config, generate_situation_fast

# ── Init ───────────────────────────────────────────────────────────────────────
app       = FastAPI(title="Language Learning AI")
templates = Jinja2Templates(directory="templates")
db.init_db()

# ── Domain contexts ────────────────────────────────────────────────────────────
DOMAIN_CONTEXTS = {
    "general":       "",
    "informatique":  "The scenario must take place in an IT/tech context (office, software project, debugging).",
    "cybersécurité": "The scenario must involve a cybersecurity situation (security audit, incident response, hacking discussion).",
    "sport":         "The scenario must take place in a sports context (gym, training session, sports club).",
    "football":      "The scenario must be related to football (match day, locker room, stadium, fan interaction).",
    "tourisme":      "The scenario must involve travel (airport, hotel, tourist attraction, asking for directions).",
    "business":      "The scenario must be in a professional business context (meeting, negotiation, job interview).",
    "médecine":      "The scenario must take place in a medical context (doctor visit, pharmacy, hospital).",
    "cuisine":       "The scenario must be in a culinary context (restaurant, market, cooking class).",
    "éducation":     "The scenario must take place in an educational setting (school, university, tutoring session).",
}


# ── Auth helper ────────────────────────────────────────────────────────────────
def _get_user(authorization: Optional[str]) -> Optional[dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    return Auth.get_current_user(token)


# ── Pydantic models ────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str
    email:    str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class SituationRequest(BaseModel):
    language: str = "French"
    level:    str = "intermediate"
    domain:   str = "general"

class ChatRequest(BaseModel):
    message:    str
    language:   str           = "French"
    level:      str           = "intermediate"
    domain:     str           = "general"
    situation:  str           = ""
    session_id: Optional[int] = None

class SaveRequest(BaseModel):
    language:   str
    level:      str           = "intermediate"
    domain:     str           = "general"
    situation:  str           = ""
    prompt:     str           = ""
    teacher:    Optional[str] = None
    styler:     Optional[str] = None
    session_id: Optional[int] = None


# ── Helpers ────────────────────────────────────────────────────────────────────
def _blank(language: str = "French", level: str = "intermediate",
           domain: str = "general") -> WorkflowState:
    return {
        "messages": [], "character": None, "teacher": None, "cultural": None,
        "styler": None, "situational": None, "mentality": None, "prompt": None,
        "history": [], "save_it": False,
        "language": language, "level": level, "domain": domain,
    }

def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

def _has_error(teacher_output: str) -> bool:
    phrases = ["no error", "no correction", "correct", "well done",
               "aucune", "pas d'erreur", "parfait", "kein fehler"]
    low = (teacher_output or "").lower()
    return not any(p in low for p in phrases)


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.post("/auth/register")
async def register(req: RegisterRequest):
    if await run_in_threadpool(db.get_user_by_username, req.username):
        return JSONResponse({"error": "Username already taken."}, status_code=400)
    if await run_in_threadpool(db.get_user_by_email, req.email):
        return JSONResponse({"error": "Email already registered."}, status_code=400)
    if len(req.password) < 6:
        return JSONResponse({"error": "Password must be at least 6 characters."}, status_code=400)

    hashed  = Auth.hash_password(req.password)
    user_id = await run_in_threadpool(db.create_user, req.username, req.email, hashed)
    token   = Auth.generate_token()
    await run_in_threadpool(db.save_token, user_id, token)

    user = await run_in_threadpool(db.get_user_by_id, user_id)
    return {"token": token, "user": {"id": user["id"], "username": user["username"], "avatar": user["avatar"]}}

@app.post("/auth/login")
async def login(req: LoginRequest):
    user = await run_in_threadpool(db.get_user_by_username, req.username)
    if not user or not Auth.verify_password(req.password, user["password"]):
        return JSONResponse({"error": "Invalid username or password."}, status_code=401)

    token = Auth.generate_token()
    await run_in_threadpool(db.save_token, user["id"], token)
    return {"token": token, "user": {"id": user["id"], "username": user["username"], "avatar": user["avatar"]}}

@app.post("/auth/logout")
async def logout(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        await run_in_threadpool(db.delete_token, token)
    return {"status": "logged out"}

@app.get("/auth/me")
async def me(authorization: Optional[str] = Header(None)):
    user = _get_user(authorization)
    if not user:
        return JSONResponse({"error": "Not authenticated."}, status_code=401)
    return {"id": user["id"], "username": user["username"], "avatar": user["avatar"], "email": user["email"]}


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/situation")
async def api_situation(req: SituationRequest,
                        authorization: Optional[str] = Header(None)):
    user       = _get_user(authorization)
    domain_ctx = DOMAIN_CONTEXTS.get(req.domain, "")
    situation  = await run_in_threadpool(
        generate_situation_fast, req.language, req.level, domain_ctx
    )
    session_id = await run_in_threadpool(
        db.create_session, req.language, req.level, situation, req.domain,
        user["id"] if user else None,
    )
    return {"situation": situation, "session_id": session_id}

@app.post("/api/chat/stream")
async def api_chat_stream(req: ChatRequest,
                          authorization: Optional[str] = Header(None)):
    user   = _get_user(authorization)
    agents = get_agents(req.level)

    async def generate():
        state: WorkflowState = {
            **_blank(req.language, req.level, req.domain),
            "messages":    [{"role": "user", "content": f"Situation: {req.situation}\n\nUser: {req.message}"}],
            "situational": req.situation,
            "prompt":      req.message,
        }
        try:
            yield _sse({"type": "status", "label": "Analysing your message…", "step": 1})

            char_r, teach_r = await asyncio.gather(
                run_in_threadpool(agents["character"].invoke, state, config),
                run_in_threadpool(agents["teacher"].invoke,   state, config),
            )
            state["character"] = char_r["messages"][-1].content
            state["teacher"]   = teach_r["messages"][-1].content

            yield _sse({"type": "status", "label": "Cultural check…", "step": 2})

            ment_r = await run_in_threadpool(agents["mentality"].invoke, state, config)
            state["mentality"] = ment_r["messages"][-1].content

            yield _sse({"type": "status", "label": "Formatting response…", "step": 3})

            styler_state = {
                **state,
                "messages": [{"role": "user", "content": (
                    "Format into clean markdown:\n\n"
                    f"**Grammar Correction**: {state['teacher']}\n\n"
                    f"**Character Response**: {state['character']}\n\n"
                    f"**Cultural Note**: {state['mentality']}"
                )}],
            }
            style_r        = await run_in_threadpool(agents["styler"].invoke, styler_state, config)
            state["styler"] = style_r["messages"][-1].content
            has_err         = _has_error(state["teacher"])

            if req.session_id:
                uid = user["id"] if user else None
                await run_in_threadpool(db.add_message, req.session_id, "user",      req.message)
                await run_in_threadpool(db.add_message, req.session_id, "assistant", state["styler"])
                if has_err:
                    await run_in_threadpool(db.add_error, req.session_id, req.message, state["teacher"], uid)

            yield _sse({"type": "done", "response": state["styler"],
                        "teacher": state["teacher"], "has_error": has_err})
        except Exception as e:
            yield _sse({"type": "error", "message": str(e)})
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.post("/api/save")
async def api_save(req: SaveRequest, authorization: Optional[str] = Header(None)):
    state: WorkflowState = {
        **_blank(req.language, req.level, req.domain),
        "situational": req.situation, "prompt": req.prompt,
        "teacher": req.teacher, "styler": req.styler,
    }
    await run_in_threadpool(save_agent, state)
    return {"status": "saved"}

@app.get("/api/stats")
async def api_stats(authorization: Optional[str] = Header(None)):
    user = _get_user(authorization)
    return await run_in_threadpool(db.get_stats, user["id"] if user else None)

@app.get("/api/errors")
async def api_errors(authorization: Optional[str] = Header(None)):
    user   = _get_user(authorization)
    errors = await run_in_threadpool(db.get_errors, user["id"] if user else None, 50)
    return {"errors": errors}

@app.get("/api/history")
async def api_history(authorization: Optional[str] = Header(None)):
    user     = _get_user(authorization)
    sessions = await run_in_threadpool(db.get_sessions, user["id"] if user else None, 20)
    return {"sessions": sessions}


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
