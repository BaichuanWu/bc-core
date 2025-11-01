import random
from datetime import datetime
from typing import List, Optional, Tuple

import pymysql
from bc_fastkit.common.typing import DATETIME_FORMAT
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.crud import (
    quants_alpha_template_handler,
    quants_wqb_alpha_handler,
    quants_wqb_data_field_handler,
)

from ..utils import ExpressionGenerator
from ..worldbrain import wqb_client


class ThreeLevelStrategy:
    def __init__(
        self,
        template_ids: Tuple[int, ...],
        batch_size: int = 10000,
        regions: Optional[list[str]] = None,
        categories: Optional[list[str]] = None,
        settings: Optional[dict] = None,
    ):
        self.batch_size = batch_size
        self.regions = regions
        self.categories = categories
        self.template_ids = list(template_ids)
        self.settings = settings or {}

    def select_data_fields(self, db: Session) -> List[models.QuantsWqbDataFieldModel]:
        pyramids_info = wqb_client.get_pyramids_alpha_info()
        if self.regions:
            pyramids_info = {
                k: v for k, v in pyramids_info.items() if k[0] in self.regions
            }
        if self.categories:
            pyramids_info = {
                k: v for k, v in pyramids_info.items() if k[2] in self.categories
            }
        rs = []
        for (region, delay, category_id), alpha_count in pyramids_info.items():
            fields, _ = quants_wqb_data_field_handler.search_limit(
                db,
                q={"region": region, "delay": delay, "category": category_id},
                order_by=[func.random()],
                limit=400 / (alpha_count + 1),
            )
            rs.extend(fields)
            random.shuffle(rs)
        return rs[: self.batch_size]

    def generate_first_level_alpha(self, db: Session):
        fields = self.select_data_fields(db)
        templates = quants_alpha_template_handler.search(
            db, q={"id": self.template_ids, "typ": 1}
        )
        batch_no = f"""{datetime.now().strftime(DATETIME_FORMAT)}_first_level"""
        # TODO fields生成修改
        for template in templates:
            print(
                f"Generating first level alphas, template: {template.title}, fields: {len(fields)}"
            )
            generator = ExpressionGenerator(
                template.expression, {**template.default_field, "data_field": fields}
            )
            for expression, field_combo in generator.generate(
                db, limit=self.batch_size
            ):
                settings = {
                    **field_combo[generator.data_field_name].settings,
                    **self.settings,
                }
                print(f"Generating expression {expression}")
                obj_in = {
                    "template_id": template.id,
                    "batch_no": batch_no,
                    "typ": template.typ,
                    "expression": expression,
                    "settings": settings,
                    "state": models.QuantsWqbAlphaModel.STATE_PENDING,
                }
                try:
                    quants_wqb_alpha_handler.create(db, obj_in=obj_in)
                    db.commit()
                except IntegrityError as e:
                    print(e)
                    if (
                        isinstance(e.orig, pymysql.err.IntegrityError)
                        and e.orig.args[0] == 1062
                    ):
                        continue
                    else:
                        raise e

    def generate_second_level_alpha(self, db: Session, filters: Optional[dict] = None):
        batch_no = f"""{datetime.now().strftime(DATETIME_FORMAT)}_second_level"""
        alphas = quants_wqb_alpha_handler.search(
            db, q={"typ": 1, "sharpe_gt": 1.2, "fitness_gt": 1, **(filters or {})}
        )
        templates = quants_alpha_template_handler.search(
            db, q={"id": self.template_ids, "typ": 2}
        )
        for template in templates:
            generator = ExpressionGenerator(
                template.expression,
                {**template.default_field, "sig1": alphas},
                data_field_name="sig1",
            )
            for expression, field_combo in generator.generate(
                db, limit=self.batch_size
            ):
                prev_alpha = field_combo[generator.data_field_name]
                settings = {**prev_alpha.settings, **self.settings}
                obj_in = {
                    "parent_id": prev_alpha.id,
                    "template_id": template.id,
                    "batch_no": batch_no,
                    "typ": template.typ,
                    "expression": expression,
                    "settings": settings,
                    "state": models.QuantsWqbAlphaModel.STATE_PENDING,
                }
                try:
                    quants_wqb_alpha_handler.create(db, obj_in=obj_in)
                except IntegrityError as e:
                    if (
                        isinstance(e.orig, pymysql.err.IntegrityError)
                        and e.orig.args[0] == 1062
                    ):
                        continue
                    else:
                        raise e

    def generate_third_level_alpha(self, db: Session, filters: Optional[dict] = None):
        batch_no = f"""{datetime.now().strftime(DATETIME_FORMAT)}_third_level"""
        alphas = quants_wqb_alpha_handler.search(
            db, q={"typ": 2, "sharpe_gt": 1.5, "fitness_gt": 1.2, **(filters or {})}
        )
        templates = quants_alpha_template_handler.search(
            db, q={"id": self.template_ids, "typ": 3}
        )
        for template in templates:
            generator = ExpressionGenerator(
                template.expression,
                {**template.default_field, "sig2": alphas},
                data_field_name="sig2",
            )
            for expression, field_combo in generator.generate(
                db, limit=self.batch_size
            ):
                prev_alpha = field_combo[generator.data_field_name]
                settings = {**prev_alpha.settings, **self.settings}
                obj_in = {
                    "parent_id": prev_alpha.id,
                    "template_id": template.id,
                    "batch_no": batch_no,
                    "typ": template.typ,
                    "expression": expression,
                    "settings": settings,
                    "state": models.QuantsWqbAlphaModel.STATE_PENDING,
                }
                try:
                    quants_wqb_alpha_handler.create(db, obj_in=obj_in)
                except IntegrityError as e:
                    if (
                        isinstance(e.orig, pymysql.err.IntegrityError)
                        and e.orig.args[0] == 1062
                    ):
                        continue
                    else:
                        raise e

    def run(self, db: Session, filters: Optional[dict] = None):
        self.generate_first_level_alpha(db)
        self.generate_second_level_alpha(db, filters)
        self.generate_third_level_alpha(db, filters)
