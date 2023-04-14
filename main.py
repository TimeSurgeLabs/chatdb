from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import Response
from sqlmodel import create_engine, SQLModel, Session

from models import Entry, SearchReq, EntryReq

# create a new FastAPI app with cors enabled
app = FastAPI(title="Database API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/get/{id}", response_model=Entry, description="Get an entry from the database via its id")
def get(id: int, request: Request):
    token = request.headers.get("Authorization", None)
    if token is None:
        return []
    # remove the bearer part from the token
    user_id = token.replace("Bearer ", "")
    with Session(engine) as session:
        # get the entry from the database
        entry = session.get(Entry, id)
        # check if the user_id matches
        if entry.user_id == user_id:
            # return the entry
            return entry
        else:
            # return an empty list
            return []


@app.post("/search", response_model=List[Entry], description="Search for an entry in the database")
def search(req: SearchReq, request: Request):
    token = request.headers.get("Authorization", None)
    if token is None:
        return []
    # remove the bearer part from the token
    user_id = token.replace("Bearer ", "")
    with Session(engine) as session:
        # search for the entry
        entries = session.query(Entry).filter(
            Entry.data.ilike(f'%{req.query.lower()}%'),
            user_id == Entry.user_id
        ).limit(10).all()
        # return the entry
        return entries


@app.post("/add", response_model=Entry, description="Add an entry to the database")
def add(entry_req: EntryReq, request: Request):
    # get the bearer token from the request
    token = request.headers.get("Authorization", None)
    if token is None:
        return []
    # remove the bearer part from the token
    user_id = token.replace("Bearer ", "")
    # get the user id from the token
    entry = Entry(data=entry_req.data.lower(), user_id=user_id)
    with Session(engine) as session:
        # add the entry to the database
        session.add(entry)
        session.commit()
        session.refresh(entry)
        # return the entry
        return entry


@app.post("/add_batch", response_model=List[Entry], description="Add a batch of entries to the database")
def add_batch(entry_reqs: List[EntryReq], request: Request):
    # get the bearer token from the request
    token = request.headers.get("Authorization", None)
    if token is None:
        return []
    # remove the bearer part from the token
    user_id = token.replace("Bearer ", "")

    # create a list to store the entries
    entries = []

    # iterate through the list of entry_reqs
    for entry_req in entry_reqs:
        # create an entry for each entry_req
        entry = Entry(data=entry_req.data.lower(), user_id=user_id)
        entries.append(entry)

    with Session(engine) as session:
        # add the entries to the database
        session.add_all(entries)
        session.commit()

        # refresh the entries and return them
        for entry in entries:
            session.refresh(entry)

        return entries


@app.get('/.well-known/ai-plugin.json', include_in_schema=False)
def read_ai_plugin_json() -> Response:
    with open('ai-plugin.json', 'r') as f:
        return Response(f.read(), media_type='application/json')
