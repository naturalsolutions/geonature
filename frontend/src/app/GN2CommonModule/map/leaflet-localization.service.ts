import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import * as L from 'leaflet';

@Injectable()
export class LeafletLocalizationService {
  constructor(private translate: TranslateService) {}

  initializeDraw() {
    (L as any).drawLocal = this.translate.instant('Map.LeafletDraw');
  }

  initializeZoom() {
    const zoom = this.translate.instant('Map.Zoom');
    const control = (L.Control as any).Zoom;
    if (control?.prototype) {
      control.prototype.options = control.prototype.options || {};
      Object.assign(control.prototype.options, {
        zoomInTitle: zoom.ZoomIn,
        zoomOutTitle: zoom.ZoomOut,
      });
    }
  }

  initializeLocate() {
    const locate = this.translate.instant('Map.Locate');
    const control = (L.Control as any).Locate;
    if (control?.prototype) {
      control.prototype.options = control.prototype.options || {};
      control.prototype.options.strings = locate;
    }
  }

  initializeFileLayer() {
    const control = (L.Control as any).FileLayerLoad;
    if (control) {
      control.TITLE = this.translate.instant('Map.FileLayer.Title');
    }
  }
}
