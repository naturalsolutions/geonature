import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { Taxon } from '@geonature_common/form/taxonomy/taxonomy.component';
import { TaxonomyComponent } from './taxonomy/taxonomy.component';

@Component({
  standalone: true,
  selector: 'infos',
  templateUrl: 'infos.component.html',
  styleUrls: ['infos.component.scss'],
  imports: [
    CommonModule,
    TaxonomyComponent
  ]
})
export class InfosComponent {
  @Input()
  taxon: Taxon;

  @Input()
  mediaUrl: any;
}
