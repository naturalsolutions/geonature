import { Component, Input } from '@angular/core';
import { IndicatorComponent } from './indicator/indicator.component';
import { InfosComponent } from './infos/infos.component';
import { CommonModule } from '@angular/common';

interface Indicator {
  name: string;
  matIcon: string;
  value: string | null;
}

@Component({
  standalone: true,
  selector: 'header',
  templateUrl: 'header.component.html',
  styleUrls: ['header.component.scss'],
  imports: [
    CommonModule,
    IndicatorComponent,
    InfosComponent
  ],
})
export class HeaderComponent {
  @Input()
  taxon: any;

  @Input()
  profile: any;

  @Input()
  mediaUrl: any;

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
        value: this.profile ? this.profile.altitude_min + 'm - ' + this.profile.altitude_max + 'm' : null,
      },
    ];
  }
}
