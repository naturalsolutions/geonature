from geonature.core.gn_commons.models import TModules
from geonature.utils.metaclass_utils import metaclass_resolver

from .imports import OcchabImportMixin


class OcchabModule(metaclass_resolver(TModules, OcchabImportMixin)):
    __mapper_args__ = {"polymorphic_identity": "occhab"}
