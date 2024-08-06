import { Component, Input } from '@angular/core';
import { GN2CommonModule } from '@geonature_common/GN2Common.module';
import { CommonModule } from '@angular/common';
import { ConfigService } from '@geonature/services/config.service';

@Component({
  standalone: true,
  selector: 'tab-map',
  templateUrl: 'tab-map.component.html',
  styleUrls: ['tab-map.component.scss'],
  imports: [GN2CommonModule, CommonModule],
})
export class TabMapComponent {
  constructor(private _config: ConfigService) {}
  area: any;

  @Input()
  set taxonInfos(taxonInfos: any) {
    this.area = taxonInfos;
  }
}
