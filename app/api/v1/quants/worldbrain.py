from bc_fastkit.api import create_commit_session_router, CRUDRequestHandler
from app.core.db import SessionDep
from app import crud, schema

router = create_commit_session_router()

@router.crud("/inspiration", 
             handler=crud.quants_inspiration_handler,
            schema=schema.quants_inspiration_schema,
            session_dep=SessionDep
             )
class InspirationRequest(CRUDRequestHandler):
    pass

@router.crud("/alpha-template",
             handler=crud.quants_alpha_template_handler,
             schema=schema.quants_alpha_template_schema,
             session_dep=SessionDep)
class AlphaTemplateRequest(CRUDRequestHandler):
    pass

@router.crud("/wqb/alpha",
             handler=crud.quants_wqb_alpha_handler,
             schema=schema.quants_wqb_alpha_schema,
             session_dep=SessionDep)
class WqbAlphaRequest(CRUDRequestHandler):
    pass

@router.crud("/wqb/alpha-template",
             handler=crud.quants_wqb_alpha_template_task_handler,
             schema=schema.quants_wqb_alpha_template_task_schema,
             session_dep=SessionDep)
class WqbAlphaTemplateTaskRequest(CRUDRequestHandler):
    pass