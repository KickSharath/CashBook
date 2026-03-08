from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import conn_mongo_client

from api.auth.router import routes as auth_routes
from api.cashbook.router import routes as cashbook_routes
from api.message_services.router import routes as message_services_routes

async def lifespan(app: FastAPI):
    app.state.mongo_client = conn_mongo_client()
    if app.state.mongo_client:
        # app.state.db = app.state.mongo_client['cashbook']
        print("MongoDB connection initialized")
    else:
        app.state.db = None
        print("Failed to connect to MongoDB")

    yield

    if app.state.mongo_client:
        app.state.mongo_client.close()
        print("MongoDB connection closed")

app = FastAPI(docs_url=None, redoc_url=None, title="Cash Book", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "https://incandescent-souffle-03646b.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes, prefix="/api/auth", tags=["Auth"])
app.include_router(cashbook_routes, prefix="/api/cashbook", tags=["CashBook"])
app.include_router(message_services_routes, prefix="/api/message", tags=["Message Services"])