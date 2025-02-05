from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import re
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def debug_log(message):
    print(f"\n🔍 DEBUG: {message}\n")

def parse_query(q: str):
    q = q.lower().strip()
    debug_log(f"Parsing query: {q}")

    if "status" in q and "ticket" in q:
        match = re.search(r"ticket (\d+)", q)
        if match:
            ticket_id = int(match.group(1))
            return "get_ticket_status", {"ticket_id": ticket_id}

    elif any(word in q for word in ["expense", "reimbursement", "emp", "balance"]):
        match = re.search(r"emp(?:loyee)? (\d+)", q)
        if match:
            employee_id = int(match.group(1))
            return "get_expense_balance", {"employee_id": employee_id}

    elif any(word in q for word in ["schedule", "book", "meeting"]):
        match = re.search(r"(?:schedule|book).+? (\d{4}-\d{2}-\d{2}) at (\d{2}:\d{2}) in (.+)", q)
        if match:
            date, time, meeting_room = match.groups()
            return "schedule_meeting", {"date": date, "time": time, "meeting_room": meeting_room}

    elif "performance bonus" in q or "bonus" in q:
        match = re.search(r"employee (\d+).+? (\d{4})", q)
        if match:
            employee_id, year = match.groups()
            return "calculate_performance_bonus", {"employee_id": int(employee_id), "current_year": int(year)}

    elif any(word in q for word in ["report", "file", "office issue"]):
        match = re.search(r"office issue (\d+) for (.+)", q)
        if match:
            issue_code = int(match.group(1))
            department = match.group(2).strip()
            return "report_office_issue", {"issue_code": issue_code, "department": department}

    return None, None

@app.get("/execute")
async def execute(q: str = Query(..., description="Query string")):
    function_name, arguments = parse_query(q)
    if function_name and arguments:
        return {
            "name": function_name,
            "arguments": json.dumps(arguments)
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid query")

if __name__ == "_main_":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)