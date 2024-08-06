import { Component, Input } from '@angular/core';
import { IndicatorComponent } from './indicator/indicator.component';
import { CommonModule } from '@angular/common';
import { ConfigService } from '@geonature/services/config.service';
import { computeIndicatorFromConfig, Indicator, IndicatorRaw } from './indicator/indicator';

@Component({
  standalone: true,
  selector: 'indicators',
  templateUrl: 'indicators.component.html',
  styleUrls: ['indicators.component.scss'],
  imports: [CommonModule, IndicatorComponent],
})
export class IndicatorsComponent {
  indicators: Array<Indicator>;
  constructor(private _config: ConfigService) {
    this.indicators = [];
  }

  @Input()
  set taxonStats(taxonStats: any) {
    if (
      this._config &&
      this._config['SYNTHESE'] &&
      this._config['SYNTHESE']['SPECIES_SHEET'] &&
      this._config['SYNTHESE']['SPECIES_SHEET']['LIST_INDICATORS']
    ) {
      this.indicators = this._config['SYNTHESE']['SPECIES_SHEET']['LIST_INDICATORS'].map(
        (indicatorConfig: IndicatorRaw) => computeIndicatorFromConfig(indicatorConfig, taxonStats)
      );
    } else {
      this.indicators = [];
    }
  }
}
