import { Component, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

@Component({
  standalone: true,
  selector: 'indicator',
  templateUrl: 'indicator.component.html',
  styleUrls: ['indicator.component.scss'],
  imports: [MatIconModule]
})
export class IndicatorComponent {
  @Input()
  name: string

  @Input()
  matIcon: string // mat-icon reference

  @Input()
  value: string

  get defaultValue(): string {
    return "-";
  }
}
