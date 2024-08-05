import { Component, Input } from '@angular/core';
import { IndicatorComponent } from './indicator/indicator.component';
import { CommonModule } from '@angular/common';

interface Indicator {
  name: string;
  matIcon: string;
  value: string | null;
}

@Component({
  standalone: true,
  selector: 'indicators',
  templateUrl: 'indicators.component.html',
  styleUrls: ['indicators.component.scss'],
  imports: [CommonModule, IndicatorComponent],
})
export class IndicatorsComponent {
  @Input()
  profile: any;

  get indicators(): Array<Indicator> {
    return [
      {
        name: 'Test',
        matIcon: 'search',
        value: '12',
      },
      {
        name: 'Observations valides',
        matIcon: 'search',
        value: this.profile?.count_valid_data,
      },

      {
        name: 'Première observation',
        matIcon: 'schedule',
        value: this.profile?.first_valid_data,
      },

      {
        name: 'Dernière observation',
        matIcon: 'search',
        value: this.profile?.last_valid_data,
      },

      {
        name: "Plage d'altitude",
        matIcon: 'terrain',
        value: this.profile
          ? this.profile.altitude_min + 'm - ' + this.profile.altitude_max + 'm'
          : null,
      },
    ];
  }
}
