import typing
from geonature.utils.env import db
from ref_geo.models import LAreas, BibAreasTypes

from geonature.core.gn_synthese.models import Synthese
from sqlalchemy import select, desc, asc, column, func
from apptax.taxonomie.models import Taxref
from geonature.core.gn_synthese.utils.query_select_sqla import SyntheseQuery
from sqlalchemy.orm import Query
from werkzeug.exceptions import BadRequest
from flask_sqlalchemy.pagination import Pagination
from enum import Enum


class SortOrder(Enum):
    ASC = "asc"
    DESC = "desc"


class TaxonSheetUtils:

    @staticmethod
    def update_query_with_sorting(query: Query, sort_by: str, sort_order: SortOrder) -> Query:
        if sort_order == SortOrder.ASC:
            return query.order_by(asc(sort_by))

        return query.order_by(desc(sort_by))

    @staticmethod
    def paginate(query: Query, page: int, per_page: int) -> Pagination:
        return query.paginate(page=page, per_page=per_page, error_out=False)

    #
    @staticmethod
    def get_cd_nom_list_from_cd_ref(cd_ref: int) -> typing.List[int]:
        return db.session.scalars(select(Taxref.cd_nom).where(Taxref.cd_ref == cd_ref))

    @staticmethod
    def get_synthese_query_with_scope(current_user, scope: int, query: Query) -> SyntheseQuery:
        synthese_query_obj = SyntheseQuery(Synthese, query, {})
        synthese_query_obj.filter_query_with_cruved(current_user, scope)
        return synthese_query_obj.query

    @staticmethod
    def is_valid_area_type(area_type: str) -> bool:
        # Ensure area_type is valid
        valid_area_types = (
            db.session.query(BibAreasTypes.type_code)
            .distinct()
            .filter(BibAreasTypes.type_code == area_type)
            .scalar()
        )

        return valid_area_types

    @staticmethod
    def get_area_subquery(area_type: str) -> Query:

        # Subquery to fetch areas based on area_type
        return (
            select(LAreas.id_area)
            .where(LAreas.id_type == BibAreasTypes.id_type, BibAreasTypes.type_code == area_type)
            .alias("areas")
        )

    @staticmethod
    def get_linnean_descendants(cd_ref_parent: int) -> typing.List[int]:
        subquery = (
            select(column("cd_ref"))
            .select_from(func.taxonomie.find_all_taxons_children(cd_ref_parent))
            .subquery()
        )

        query = select(subquery.c.cd_ref).distinct()

        result = db.session.execute(query)
        return [row[0] for row in result]

    @staticmethod
    def get_taxon_list(cd_ref: int, has_linnean_descendants: bool) -> typing.List[int]:
        if has_linnean_descendants:
            taxref_cd_nom_list = TaxonSheetUtils.get_linnean_descendants(cd_ref)
            if not taxref_cd_nom_list:
                taxref_cd_nom_list = TaxonSheetUtils.get_cd_nom_list_from_cd_ref(cd_ref)
        else:
            taxref_cd_nom_list = TaxonSheetUtils.get_cd_nom_list_from_cd_ref(cd_ref)
        return taxref_cd_nom_list
