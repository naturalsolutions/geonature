import { Component, Input } from '@angular/core';
import { GN2CommonModule } from '@geonature_common/GN2Common.module';
import { CommonModule } from '@angular/common';
import { ConfigService } from '@geonature/services/config.service';
import { TabMapComponent } from './tab-map/tab-map.component';

enum TABS {
  MAP = 'map',
}

@Component({
  standalone: true,
  selector: 'advanced-infos',
  templateUrl: 'advanced-infos.component.html',
  styleUrls: ['advanced-infos.component.scss'],
  imports: [GN2CommonModule, CommonModule, TabMapComponent],
})
export class AdvancedDetailsComponent {
  tabRequired: boolean;
  selectedIndex: number;

  constructor(private _config: ConfigService) {}

  get tabsProperties(): any {
    return {
      [TABS.MAP]: this._config['SYNTHESE']['SPECIES_SHEET']['TAB_MAP'],
    };
  }

  @Input()
  taxonInfos: any;
}
