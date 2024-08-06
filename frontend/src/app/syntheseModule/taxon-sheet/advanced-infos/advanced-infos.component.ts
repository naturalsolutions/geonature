import { Component, Input } from '@angular/core';
import { GN2CommonModule } from '@geonature_common/GN2Common.module';
import { CommonModule } from '@angular/common';

@Component({
  standalone: true,
  selector: 'advanced-infos',
  templateUrl: 'advanced-infos.component.html',
  styleUrls: ['advanced-infos.component.scss'],
  imports: [GN2CommonModule, CommonModule],
})
export class AdvancedDetailsComponent {
  tabRequired: boolean;
  selectedIndex: number;

  @Input()
  taxonInfos: any;
}
