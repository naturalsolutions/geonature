import { Component, Input, OnInit } from '@angular/core';
import { GN2CommonModule } from '@geonature_common/GN2Common.module';
import { CommonModule } from '@angular/common';
import { MapListService } from '@geonature_common/map-list/map-list.service';
import { Taxon } from '@geonature_common/form/taxonomy/taxonomy.component';
import {
  SyntheseDataService,
  TaxonStats,
} from '@geonature_common/form/synthese-form/synthese-data.service';
import { FeatureCollection } from 'geojson';
import { TaxonSheetService } from '../taxon-sheet.service';
import { ConfigService } from '@geonature/services/config.service';
import * as L from 'leaflet';
import { SyntheseFormService } from '@geonature_common/form/synthese-form/synthese-form.service';
import { TranslateService } from '@ngx-translate/core';
import { MapService } from '@geonature_common/map/map.service';
import { MatSliderModule } from '@angular/material/slider';
import { Loadable } from '../loadable';
import { finalize } from 'rxjs/operators';
import { CommonService } from '@geonature_common/service/common.service';
import { AreasService } from '@geonature/syntheseModule/synthese-results/synthese-carte/areas-service/areas.service';

interface YearInterval {
  min: number;
  max: number;
}

@Component({
  standalone: true,
  selector: 'tab-geographic-overview',
  templateUrl: 'tab-observations.component.html',
  styleUrls: ['tab-observations.component.scss'],
  imports: [GN2CommonModule, CommonModule, MatSliderModule],
  providers: [AreasService],
})
export class TabObservationsComponent extends Loadable implements OnInit {
  observations: FeatureCollection | null = null;
  taxon: Taxon | null = null;

  yearIntervalBoundaries: YearInterval | null = null;
  yearInterval: YearInterval | null = null;

  private isSuperiorToSyntheseLimit: Boolean = false;

  constructor(
    private _syntheseDataService: SyntheseDataService,
    private _tss: TaxonSheetService,
    public mapListService: MapListService,
    public config: ConfigService,
    public formService: SyntheseFormService,
    public translateService: TranslateService,
    private _ms: MapService,
    private _commonService: CommonService,
    private _areasService: AreasService
  ) {
    super();
  }

  formatLabel(value: number): string {
    return `${value}`;
  }

  ngOnInit() {
    this._tss.taxon.subscribe((taxon: Taxon | null) => {
      this.taxon = taxon;
      if (!taxon) {
        return;
      }
      this.updateTabObservations();
    });

    this._areasService.areasEnable.subscribe((enable: boolean) => {
      this.updateTabObservations();
    });


    this._tss.taxonStats.subscribe((stats: TaxonStats | null) => {
      this.updateTaxonStats(stats);
    });
  }

  updateTaxonStats(stats: TaxonStats | null) {
    if (!stats) {
      this.yearIntervalBoundaries = null;
      this.yearInterval = null;
      return;
    }
    this.isSuperiorToSyntheseLimit =
      stats.observation_count > this.config['SYNTHESE']['NB_MAX_OBS_MAP'];

    this.yearIntervalBoundaries = {
      min: new Date(stats.date_min).getFullYear(),
      max: new Date(stats.date_max).getFullYear(),
    };

    this.yearInterval = { ...this.yearIntervalBoundaries };
  }

  updateTabObservations() {
    if (!this.taxon) {
      return;
    }
    this.startLoading();
    const areasEnable = this._areasService.areasEnable.value;

    const filter: {
      cd_ref: number[];
      cd_ref_parent: number[];
      date_min?: string;
      date_max?: string;
    } = {
      cd_ref: [this.taxon.cd_ref],
      cd_ref_parent: [this.taxon.cd_ref],
    };
    if (this.yearInterval) {
      filter.date_min = `${this.yearInterval.min}-01-01`;
      filter.date_max = `${this.yearInterval.max}-12-31`;
    }
    const limit = areasEnable ? -1 : undefined;
    const format = this._areasService.format;

    this._syntheseDataService
      .getSyntheseData({ filter }, { format, limit })
      .pipe(finalize(() => this.stopLoading()))
      .subscribe((data) => {
        if (!areasEnable && this.isSuperiorToSyntheseLimit) {
          this._commonService.regularToaster(
            'warning',
            `Pour des raisons de performances, le nombre d'observations affichées est limité à ${this.config['SYNTHESE']['NB_MAX_OBS_MAP']}`
          );
        }
        this._areasService.styleTabGeoJson = undefined;
        const map = this._ms.map;

        map.eachLayer((layer) => {
          if (!(layer instanceof L.TileLayer)) {
            map.removeLayer(layer);
          }
        });

        if (data) {
          const geoJSON = L.geoJSON(data, {
            pointToLayer: (feature, latlng) => {
              const circleMarker = L.circleMarker(latlng, {
                radius: 10,
              });
              return circleMarker;
            },
            onEachFeature: this.onEachFeature.bind(this),
          });

          this._ms.map.addLayer((L as any).markerClusterGroup().addLayer(geoJSON));
          this._ms.map.fitBounds(geoJSON.getBounds());
        }
      });
  }

  onEachFeature(feature, layer) {
    const observations = feature.properties.observations;
    let popupContent = '';

    if (observations && observations.length > 0) {
      if (this._areasService.areasEnable && feature.geometry.type === 'MultiPolygon') {
        const obsCount = observations.length;
        this._areasService.setAreasStyle(layer as L.Path, obsCount);
        popupContent = `${obsCount} observations`;
      } else {
        popupContent = `
          ${observations[0].nom_vern_or_lb_nom || ''}<br>
          <b>Observé le :</b> ${observations[0].date_min || 'Non défini'}<br>
          <b>Par :</b> ${observations[0].observers || 'Non défini'}
        `;
      }

      layer.bindPopup(popupContent);

      layer.on('click', function () {
        this.openPopup();
      });
    }
  }

  get styleTabGeoJson() {
    return this._areasService.styleTabGeoJson
  }

  ngAfterViewInit() {
    this._areasService.updateView();
  }
}
