import os
from apptax.admin.admin_view import (
    BibListesView,
    TaxrefView,
    TMediasView,
    BibAttributsView,
    BibThemesView,
    SummaryView,
)
from geonature.utils.env import db

from apptax.admin.admin import adresses
from apptax.taxonomie.models import Taxref, BibListes, TMedias, BibAttributs, BibThemes
from geonature.core.admin.utils import CruvedProtectedMixin
from flask_babel import lazy_gettext as _l


class CruvedProtectedBibListesView(CruvedProtectedMixin, BibListesView):
    module_code = "TAXHUB"
    object_code = "LISTES"
    extra_actions_perm = {".import_cd_nom_view": "C"}


class CruvedProtectedTaxrefView(CruvedProtectedMixin, TaxrefView):
    module_code = "TAXHUB"
    object_code = "TAXONS"


class CruvedProtectedTMediasView(CruvedProtectedMixin, TMediasView):
    module_code = "TAXHUB"
    object_code = "TAXONS"


class CruvedProtectedBibAttributsView(CruvedProtectedMixin, BibAttributsView):
    module_code = "TAXHUB"
    object_code = "ATTRIBUTS"


class CruvedProtectedBibThemes(CruvedProtectedMixin, BibThemesView):
    module_code = "TAXHUB"
    object_code = "THEMES"


class CruvedProtectedSummaryView(CruvedProtectedMixin, SummaryView):
    module_code = "TAXHUB"
    object_code = "TAXONS"


def load_admin_views(app, admin):
    static_folder = os.path.join(adresses.root_path, "static")

    admin.add_view(
        CruvedProtectedTaxrefView(
            Taxref,
            db.session,
            name="Taxref",
            endpoint="taxons",
            category="TaxHub",
            static_folder=static_folder,
        )
    )
    admin.add_view(
        CruvedProtectedBibListesView(
            BibListes,
            db.session,
            name=_l("Listes"),
            category="TaxHub",
            static_folder=static_folder,
        )
    )

    admin.add_view(
        CruvedProtectedBibAttributsView(
            BibAttributs,
            db.session,
            name=_l("Attributs"),
            category="TaxHub",
            static_folder=static_folder,
        )
    )
    admin.add_view(
        CruvedProtectedBibThemes(
            BibThemes,
            db.session,
            name=_l("Thèmes"),
            category="TaxHub",
            static_folder=static_folder,
        )
    )

    admin.add_view(
        CruvedProtectedTMediasView(
            TMedias,
            db.session,
            name=_l("Médias"),
            category="TaxHub",
            static_folder=static_folder,
        )
    )
    admin.add_view(
        CruvedProtectedSummaryView(
            name="Informations",
            endpoint="summary",
            category="TaxHub",
            static_folder=static_folder,
        )
    )
