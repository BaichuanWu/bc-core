from fastapi import APIRouter 
from app.core.db import  SessionDep
from app.models.quants import QuantsAlphaRecordModel
from bc_fastkit.crud import CRUDBase
from typing import List
from bc_fastkit.schema import create_default_cru_schema

router = APIRouter()

record_schema = create_default_cru_schema(
    QuantsAlphaRecordModel)

crud_record = CRUDBase(QuantsAlphaRecordModel)

@router.get("/", response_model=List[record_schema.R])
async def get_alphas(db: SessionDep):
    rs = crud_record.search(db, {})
    print(rs)
    return rs

