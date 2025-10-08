from bc_fastkit.crud import CRUDBase
from app.models.quants import (
    QuantsAlphaTemplateModel,
    QuantsWqbAlphaModel,
    QuantsWqbAlphaTemplateTaskModel,
    QuantsInspirationModel
)

quants_inspiration_handler = CRUDBase(QuantsInspirationModel)
quants_alpha_template_handler = CRUDBase(QuantsAlphaTemplateModel)
quants_wqb_alpha_handler = CRUDBase(QuantsWqbAlphaModel)
quants_wqb_alpha_template_task_handler = CRUDBase(QuantsWqbAlphaTemplateTaskModel)
