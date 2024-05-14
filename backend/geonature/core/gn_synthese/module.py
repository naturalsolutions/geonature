from geonature.core.gn_commons.models import TModules

from geonature.core.gn_synthese.imports import SyntheseImportMixin
from geonature.utils.metaclass_utils import metaclass_resolver


class SyntheseModule(metaclass_resolver(TModules, SyntheseImportMixin)):
    __mapper_args__ = {"polymorphic_identity": "synthese"}
