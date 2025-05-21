import { Injectable } from "@angular/core";
import { ConfigService } from "@geonature/services/config.service";
import { MapService } from "@geonature_common/map/map.service";
import { BehaviorSubject } from "rxjs";
import * as L from 'leaflet';
import { takeUntil } from 'rxjs/operators';
import { LangChangeEvent, TranslateService } from '@ngx-translate/core';
import { Subject } from 'rxjs';

interface MapAreasStyle {
  color: string;
  weight: number;
  fillOpacity: number;
  fillColor?: string;
}

enum FORMAT {
  GROUPED_GEOM_BY_AREAS = 'grouped_geom_by_areas',
  GROUPED_GEOM = 'grouped_geom',
}

@Injectable()
export class AreasService {
  areasEnable: BehaviorSubject<boolean>;
  areasLegend: any;

  styleTabGeoJson: {};

  private destroy$: Subject<boolean> = new Subject<boolean>();

  private _areasLabelSwitchBtn;

  readonly MAP_AREA_STYLE: MapAreasStyle = {
    color: '#FFFFFF',
    weight: 0.4,
    fillOpacity: 0.8,
  };

  readonly MAP_AREAS_STYLE_ACTIVE: MapAreasStyle = {
    color: '#FFFFFF',
    weight: 0.4,
    fillOpacity: 0.3,
  };

  get format(): string {
    return this.areasEnable.value ? FORMAT.GROUPED_GEOM_BY_AREAS : FORMAT.GROUPED_GEOM;
  }

  constructor(
    private _ms: MapService,
    public translateService: TranslateService,
    private _config: ConfigService
  ) {
    this.areasEnable = new BehaviorSubject<boolean>(this._config.SYNTHESE.AREA_AGGREGATION_BY_DEFAULT);
  }

  addAreasButton() {
    const LayerControl = L.Control.extend({
      options: {
        position: 'topright',
      },
      onAdd: (map) => {
        let switchBtnContainer = L.DomUtil.create(
          'div',
          'leaflet-bar custom-control custom-switch leaflet-control-custom synthese-map-areas'
        );

        let switchBtn = L.DomUtil.create('input', 'custom-control-input', switchBtnContainer);
        switchBtn.id = 'toggle-areas-btn';
        switchBtn.type = 'checkbox';
        switchBtn.checked = this.areasEnable.value;

        switchBtn.onclick = () => {
          this.areasEnable.next(switchBtn.checked);
          if (this.areasEnable.value) {
            this.addAreasLegend();
          } else {
            this.removeAreasLegend();
          }
        };

        this._areasLabelSwitchBtn = L.DomUtil.create(
          'label',
          'custom-control-label',
          switchBtnContainer
        );
        this._areasLabelSwitchBtn.setAttribute('for', 'toggle-areas-btn');
        this._areasLabelSwitchBtn.innerText = this.translateService.instant(
          'Synthese.Map.AreasToggleBtn'
        );

        return switchBtnContainer;
      },
    });

    const map = this._ms.getMap();
    map.addControl(new LayerControl());
  }

  private addAreasLegend() {
    if (this.areasLegend) return;
    this.areasLegend = new (L.Control.extend({
      options: { position: 'bottomright' },
    }))();

    this.areasLegend.onAdd = (map: L.Map): HTMLElement => {
      let div: HTMLElement = L.DomUtil.create('div', 'info legend');
      let grades: number[] = this._config['SYNTHESE']['AREA_AGGREGATION_LEGEND_CLASSES']
        .map((legendClass: { min: number; color: string }) => legendClass.min)
        .reverse();
      let labels: string[] = ["<strong> Nombre <br> d'observations </strong> <br>"];

      for (let i = 0; i < grades.length; i++) {
        labels.push(
          '<i style="background:' +
            this.getColor(grades[i] + 1) +
            '"></i> ' +
            grades[i] +
            (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+')
        );
      }
      div.innerHTML = labels.join('<br>');

      return div;
    };

    const map = this._ms.getMap();
    this.areasLegend.addTo(map);
  }

  private removeAreasLegend() {
    if (this.areasLegend) {
      const map = this._ms.getMap();
      map.removeControl(this.areasLegend);
      this.areasLegend = null;
    }
  }

  public setAreasStyle(layer: L.Layer, obsNbr: number) {
    if (layer instanceof L.Path) {
      this.MAP_AREA_STYLE['fillColor'] = this.getColor(obsNbr);
      layer.setStyle(this.MAP_AREA_STYLE);
      delete this.MAP_AREA_STYLE['fillColor'];
      this.styleTabGeoJson = this.MAP_AREAS_STYLE_ACTIVE;
    }
  }

  private getColor(obsNbr: number) {
    let classesNbr = this._config['SYNTHESE']['AREA_AGGREGATION_LEGEND_CLASSES'].length;
    let lastIndex = classesNbr - 1;
    for (let i = 0; i < classesNbr; i++) {
      let legendClass = this._config['SYNTHESE']['AREA_AGGREGATION_LEGEND_CLASSES'][i];
      if (i != lastIndex) {
        if (obsNbr > legendClass.min) {
          return legendClass.color;
        }
      } else {
        return legendClass.color;
      }
    }
  }

  public updateView() {
    this.addAreasButton();
    this.onLanguageChange();
    if (this.areasEnable.value) {
      this.addAreasLegend();
    }
  }

  private onLanguageChange() {
    // don't forget to unsubscribe!
    this.translateService.onLangChange
      .pipe(takeUntil(this.destroy$))
      .subscribe((langChangeEvent: LangChangeEvent) => {
        this.defineI18nMessages();
      });
  }

  private defineI18nMessages() {
    // Define default messages for datatable
    this.translateService
      .get('Synthese.Map.AreasToggleBtn')
      .subscribe((translatedTxt: string[]) => {
        this._areasLabelSwitchBtn.innerText = translatedTxt;
      });
  }
}
