import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { Taxon } from '@geonature_common/form/taxonomy/taxonomy.component';

// ////////////////////////////////////////////////////////////////////////////
// TO IMPROVE
// ////////////////////////////////////////////////////////////////////////////

enum TaxonomyRankId {
  REGNE = 0,
  PHYLUM = 1,
  CLASSE = 2,
  ORDRE = 3,
  FAMILLE = 4,
  NOM = 5
}
interface TaxonomyRank {
  rankId: TaxonomyRankId
  label: string
  value: string
}

// The entry in the TAXON object
const TAXONOMY_RANK_IN_TAXON: Record<TaxonomyRankId, string> = {
  [TaxonomyRankId.REGNE]: "regne",
  [TaxonomyRankId.PHYLUM]: "phylum",
  [TaxonomyRankId.CLASSE]: "classe",
  [TaxonomyRankId.ORDRE]: "ordre",
  [TaxonomyRankId.FAMILLE]: "famille",
  [TaxonomyRankId.NOM]: "nom_complet",
}

// The entry in the TAXON object
const TAXONOMY_RANK_LABEL: Record<TaxonomyRankId, string> = {
  [TaxonomyRankId.REGNE]: "règne",
  [TaxonomyRankId.PHYLUM]: "phylum",
  [TaxonomyRankId.CLASSE]: "classe",
  [TaxonomyRankId.ORDRE]: "ordre",
  [TaxonomyRankId.FAMILLE]: "famille",
  [TaxonomyRankId.NOM]: "nom latin",
}


function sortByTaxonomyRank(taxonomy: Array<TaxonomyRank>){
  taxonomy.sort((a: TaxonomyRank, b:TaxonomyRank) => {
    if(a.rankId === b.rankId) {
      return 0;
    }
    return a.rankId < b.rankId ? -1 : 1;
  })
}

// ////////////////////////////////////////////////////////////////////////////
// TO IMPROVE
// ////////////////////////////////////////////////////////////////////////////

@Component({
  standalone: true,
  selector: 'taxonomy',
  templateUrl: 'taxonomy.component.html',
  styleUrls: ['taxonomy.component.scss'],
  imports: [
    CommonModule
  ]
})
export class TaxonomyComponent {
  taxonomy: Array<TaxonomyRank>;

  @Input()
  set taxon(taxon: Taxon) {
    this.taxonomy = [];

    // Setup the taxonomy tree
    if(taxon){
      for(const rank of Object.keys(TAXONOMY_RANK_IN_TAXON) as unknown as Array<TaxonomyRankId>){
        const key = TAXONOMY_RANK_IN_TAXON[rank]
        if(taxon[key]){
          this.taxonomy.push({
            rankId: rank as TaxonomyRankId,
            label: TAXONOMY_RANK_LABEL[rank],
            value: taxon[key]
          })
        }
      }
      sortByTaxonomyRank(this.taxonomy);
    }
  }
}
