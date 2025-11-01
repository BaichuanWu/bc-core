from bc_fastkit.crud import CRUDBase
from sqlalchemy.orm import Session

from app.models.quants import (
    QuantsAlphaTemplateModel,
    QuantsInspirationModel,
    QuantsWqbAlphaModel,
    QuantsWqbAlphaTaskModel,
    QuantsWqbDataFieldModel,
    QuantsWqbOperatorModel,
    QuantsWqbUniverseModel,
)
from app.utils import convert_iso_time_str_to_datetime


class CRUDWqbAlphaTemplateTask(CRUDBase):
    def generate_wqb_alpha(self, db, *, id):
        pass


class CRUDWqbAlpha(CRUDBase[QuantsWqbAlphaModel]):

    def complement_obj_in(self, db: Session, *, obj_in):
        if "expression" in obj_in:
            obj_in["expression"] = self.model.normalize_expr(obj_in["expression"])
        if "settings" in obj_in:
            settings = obj_in["settings"]
            obj_in["region"] = settings["region"]
            obj_in["universe"] = settings["universe"]
            obj_in["delay"] = settings["delay"]
        if "wqb_data" in obj_in:
            obj_in["sharpe"] = (obj_in["wqb_data"]["is"]["sharpe"],)
            obj_in["fitness"] = obj_in["wqb_data"]["is"]["fitness"]
        if "settings" in obj_in and "expression" in obj_in:
            obj_in["expression_hash"] = self.model.generate_expression_hash(
                obj_in["expression"], obj_in["settings"]
            )
        return super().complement_obj_in(db, obj_in=obj_in)

    def get_by_expression_and_settings(
        self, db: Session, *, expression: str, settings: dict
    ) -> QuantsWqbAlphaModel | None:
        expression_hash = self.model.generate_expression_hash(expression, settings)
        print("Searching for expression hash:", expression_hash)
        return (
            db.query(self.model)
            .filter(self.model.expression_hash == expression_hash)
            .first()
        )

    def create_or_update_by_wqb_data(
        self, db: Session, *, data: dict
    ) -> QuantsWqbAlphaModel:
        obj_in = {
            "wqb_alpha_id": data["id"],
            "expression": data["regular"]["code"],
            "operator_count": data["regular"]["operatorCount"],
            "description": data["regular"].get("description", "") or "",
            "region": data["settings"]["region"],
            "universe": data["settings"]["universe"],
            "delay": data["settings"]["delay"],
            "wqb_data": data,
            "wqb_create_time": data.get("dateCreated")
            and convert_iso_time_str_to_datetime(data["dateCreated"]),
            "wqb_modified_time": data.get("dateModified")
            and convert_iso_time_str_to_datetime(data["dateModified"]),
            "wqb_submitted_time": data.get("dateSubmitted")
            and convert_iso_time_str_to_datetime(data["dateSubmitted"]),
            "settings": data["settings"],
        }
        state = quants_wqb_alpha_handler.model.state_from_str(data["status"])

        prev = quants_wqb_alpha_handler.search_one(
            db, q={"wqb_alpha_id": obj_in["wqb_alpha_id"]}
        )
        if not prev:
            prev = quants_wqb_alpha_handler.get_by_expression_and_settings(
                db,
                expression=obj_in["expression"],
                settings=obj_in["settings"],
            )

        if prev:
            if state > prev.state:
                obj_in["state"] = state
            return quants_wqb_alpha_handler.update(
                db,
                obj_in=obj_in | {"id": prev.id},
            )
        else:
            return quants_wqb_alpha_handler.create(db, obj_in=obj_in)


class CRUDWqbDataField(CRUDBase[QuantsWqbDataFieldModel]):
    def create_or_update_by_wqb_data(
        self, db: Session, *, data: dict
    ) -> QuantsWqbDataFieldModel:
        obj_in = {
            "region": data["region"],
            "delay": data["delay"],
            "universe": data["universe"],
            "dataset_id": data["dataset"]["id"],
            "typ": quants_wqb_data_field_handler.model.typ_from_str(data["type"]),
            "category": data["category"]["id"],
            "sub_category": data.get("subcategory", {}).get("id") or "",
            "name": data["id"],
            "description": data["description"],
            "payramid_multiplier": data["pyramidMultiplier"],
            "coverage": data["coverage"],
            "user_count": data["userCount"],
            "alpha_count": data["alphaCount"],
        }
        prev = quants_wqb_data_field_handler.search_one(
            db,
            q={
                "region": obj_in["region"],
                "universe": obj_in["universe"],
                "delay": obj_in["delay"],
                "dataset_id": obj_in["dataset_id"],
                "name": obj_in["name"],
            },
        )
        if prev:
            return quants_wqb_data_field_handler.update(
                db,
                obj_in={**obj_in, "id": prev.id},
            )
        else:
            return quants_wqb_data_field_handler.create(db, obj_in=obj_in)


quants_inspiration_handler = CRUDBase(QuantsInspirationModel)
quants_alpha_template_handler = CRUDBase(QuantsAlphaTemplateModel)
quants_wqb_alpha_handler = CRUDWqbAlpha(QuantsWqbAlphaModel)
quants_wqb_alpha_task_handler = CRUDWqbAlphaTemplateTask(QuantsWqbAlphaTaskModel)
quants_wqb_operator_handler = CRUDBase(QuantsWqbOperatorModel)
quants_wqb_data_field_handler = CRUDWqbDataField(QuantsWqbDataFieldModel)
quants_wqb_universe_handler = CRUDBase(QuantsWqbUniverseModel)
