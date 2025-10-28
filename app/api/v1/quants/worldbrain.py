from bc_fastkit.api import CRUDRequestHandler, create_commit_session_router

from app import crud, schema
from app.core.db import SessionDep
from app.services.quants.worldbrain import wqb_client

router = create_commit_session_router()


@router.crud(
    "/inspiration",
    handler=crud.quants_inspiration_handler,
    schema=schema.quants_inspiration_schema,
    session_dep=SessionDep,
)
class InspirationRequest(CRUDRequestHandler):
    pass


@router.crud(
    "/template",
    handler=crud.quants_alpha_template_handler,
    schema=schema.quants_alpha_template_schema,
    session_dep=SessionDep,
)
class AlphaTemplateRequest(CRUDRequestHandler):
    pass


@router.crud(
    "/wqb/alpha",
    handler=crud.quants_wqb_alpha_handler,
    schema=schema.quants_wqb_alpha_schema,
    session_dep=SessionDep,
)
class WqbAlphaRequest(CRUDRequestHandler):
    pass


@router.crud(
    "/wqb/alpha-template",
    handler=crud.quants_wqb_alpha_task_handler,
    schema=schema.quants_wqb_alpha_task_schema,
    session_dep=SessionDep,
)
class WqbAlphaTemplateTaskRequest(CRUDRequestHandler):
    pass


@router.get("/wqb/operator-list", response_model=schema.quants_wqb_operator_schema.QR)
async def get_wqb_operator_list(db: SessionDep):
    data, total = crud.quants_wqb_operator_handler.search_limit(db, {})
    return {"dataSource": data, "total": total}


@router.post("/wqb/operator-list", response_model=schema.quants_wqb_operator_schema.QR)
async def refresh_wqb_operator_list(db: SessionDep):
    wqb_client.sync_operators(db)
    data, total = crud.quants_wqb_operator_handler.search_limit(db, {})
    return {"dataSource": data, "total": total}


# @router.get("/wqb/dataset")
# async def get_wqb_dataset(db: SessionDep, common=Depends(CommonQueryParams)):
#     resp = wqb_client.get_dataset_list(
#         region=common.q.get("region"),
#         delay=common.q.get("delay"),
#         universe=common.q.get("universe"),
#         dataset_id=common.q.get("dataset_id"),
#         offset=common.skip,
#         limit=common.limit,
#     )
#     data = resp.json()
#     return {"dataSource": data["results"], "total": data["count"]}
