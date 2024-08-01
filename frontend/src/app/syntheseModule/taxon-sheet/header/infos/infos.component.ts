import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  standalone: true,
  selector: 'infos',
  templateUrl: 'infos.component.html',
  styleUrls: ['infos.component.scss'],
  imports: [
    CommonModule
  ]
})
export class InfosComponent {
  @Input()
  taxon: any;

  @Input()
  mediaUrl: any;
}
