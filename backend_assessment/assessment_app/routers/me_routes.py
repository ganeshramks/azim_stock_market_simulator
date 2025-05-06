from fastapi import APIRouter

router = APIRouter(prefix="/me")

@router.get("/test")
async def test_authenticated():
    return {"message": "Authenticated!"}
