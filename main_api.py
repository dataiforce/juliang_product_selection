from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from db.manage.base import get_db
from db.manage.selection import get_unprocessed_promotion, set_roi_check
import uvicorn
from typing import Optional


app = FastAPI()


@app.get("/unprocessed-promotion")
def api_get_unprocessed_promotion(session: Session = Depends(get_db)):
    result = get_unprocessed_promotion(session)
    if not result:
        return {"message": "No unprocessed promotion"}
    return result


@app.get("/set-roi-check")
def api_set_roi_check(
    promotion_id: str = Query(...),
    roi_status: int = Query(...),
    roi: Optional[float] = Query(None),
    session: Session = Depends(get_db)
):
    set_roi_check(session, promotion_id, roi_status, roi)
    return {"message": f"ROI check updated to {roi_status}:{roi} for promotion {promotion_id}"}



if __name__ == "__main__":
    uvicorn.run("main_api:app", host="0.0.0.0", port=8000, reload=True)