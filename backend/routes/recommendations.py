from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import RecommendationOut
from services.recommendation_service import get_active_recommendations, regenerate_recommendations

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("", response_model=list[RecommendationOut])
def list_recommendations(db: Session = Depends(get_db)):
    return get_active_recommendations(db)


@router.post("/generate", response_model=list[RecommendationOut])
async def generate_recommendations(db: Session = Depends(get_db)):
    return await regenerate_recommendations(db)
