#!/usr/bin/env python3
"""
Simple FastAPI + Strawberry GraphQL test server
to verify basic functionality before running full backend
"""

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from FastAPI + Strawberry GraphQL!"

schema = strawberry.Schema(query=Query)

app = FastAPI(title="JobQuest Navigator Test API")

# Add GraphQL router
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def root():
    return {"message": "FastAPI + Strawberry GraphQL is working!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)