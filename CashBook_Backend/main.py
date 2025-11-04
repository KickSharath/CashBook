from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routes.cashbook_apis, routes.auth_apis
from core.database import conn_mongo_client

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

app = FastAPI(docs_url=None, redoc_url=None, title="Lekka Book", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.cashbook_apis.routes, prefix="/api/cashbook", tags=["CashBook"])
app.include_router(routes.auth_apis.routes, prefix="/api/auth", tags=["Auth"])