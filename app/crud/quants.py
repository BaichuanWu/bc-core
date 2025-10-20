from bc_fastkit.crud import CRUDBase

from app.models.quants import (
    QuantsAlphaTemplateModel,
    QuantsInspirationModel,
    QuantsWqbAlphaModel,
    QuantsWqbAlphaTaskModel,
    QuantsWqbOperatorModel,
)


class CRUDWqbAlphaTemplateTask(CRUDBase):
    def generate_wqb_alpha(self, db, *, id):
        pass


quants_inspiration_handler = CRUDBase(QuantsInspirationModel)
quants_alpha_template_handler = CRUDBase(QuantsAlphaTemplateModel)
quants_wqb_alpha_handler = CRUDBase(QuantsWqbAlphaModel)
quants_wqb_alpha_task_handler = CRUDWqbAlphaTemplateTask(QuantsWqbAlphaTaskModel)
quants_wqb_operator_handler = CRUDBase(QuantsWqbOperatorModel)
