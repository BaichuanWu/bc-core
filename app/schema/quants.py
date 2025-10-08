from bc_fastkit.schema import create_default_cru_schema

from app.models.quants import (
    QuantsAlphaTemplateModel,
    QuantsInspirationModel,
    QuantsWqbAlphaModel,
    QuantsWqbAlphaTemplateTaskModel,
)

quants_inspiration_schema = create_default_cru_schema(QuantsInspirationModel)
quants_alpha_template_schema = create_default_cru_schema(QuantsAlphaTemplateModel)
quants_wqb_alpha_schema = create_default_cru_schema(QuantsWqbAlphaModel)
quants_wqb_alpha_template_task_schema = create_default_cru_schema(
    QuantsWqbAlphaTemplateTaskModel
)
