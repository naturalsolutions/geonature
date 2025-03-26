import { Component, OnInit, ViewChild } from '@angular/core';
import { FormControl, Validators } from '@angular/forms';
import { FieldMapping } from '@geonature/modules/imports/models/mapping.model';

import { FieldMappingService } from '@geonature/modules/imports/services/mappings/field-mapping.service';
import { skip } from 'rxjs/operators';
import { ImportProcessService } from '../../import-process.service';
import { Cruved, toBooleanCruved } from '@geonature/modules/imports/models/cruved.model';
import { CruvedStoreService } from '@geonature_common/service/cruved-store.service';
import { Subscription } from 'rxjs';
import { ConfigService } from '@geonature/services/config.service';

@Component({
  selector: 'pnx-mapping-selection',
  templateUrl: './mapping-selection.component.html',
  styleUrls: ['./mapping-selection.component.scss'],
})
export class MappingSelectionComponent implements OnInit {
  public userFieldMappings: Array<FieldMapping> = [];
  public fieldMappingForm: FormControl;
  public createOrRenameMappingForm = new FormControl(null, [Validators.required]); // form to add a new mapping

  public cruved: Cruved;

  private fieldMappingSub: Subscription;

  @ViewChild('deleteConfirmModal') deleteConfirmModal;

  constructor(
    private _fm: FieldMappingService,
    private _importProcessService: ImportProcessService,
    public cruvedStore: CruvedStoreService,
    private _config: ConfigService
  ) {
    this.cruved = toBooleanCruved(this.cruvedStore.cruved.IMPORT.module_objects.MAPPING.cruved);
    this.fieldMappingForm = this._fm.mappingSelectionFormControl;
  }

  ngOnInit() {
    this._fm.data.subscribe(({ fieldMappings, targetFields, sourceFields }) => {
      if (!fieldMappings) return;
      this.userFieldMappings = fieldMappings;
    });
    this.fieldMappingForm.setValue(null);
    this._fm.currentFieldMapping.next(null);
    this.fieldMappingSub = this.fieldMappingForm.valueChanges
      .pipe(
        // skip first empty value to avoid reseting the field form if importData as mapping:
        skip(this._importProcessService.getImportData().fieldmapping === null ? 0 : 1)
      )
      .subscribe((mapping: FieldMapping) => {
        this.onNewMappingSelected(mapping);
      });
  }

  ngOnDestroy() {
    this.fieldMappingSub.unsubscribe();
  }

  /**
   * Callback when a new mapping is selected
   *
   * @param {FieldMapping} mapping - the selected mapping
   */
  onNewMappingSelected(mapping: FieldMapping = null): void {
    this._fm.currentFieldMapping.next(mapping);
  }

  isMappingSelected(): boolean {
    return this.fieldMappingForm.value != null;
  }

  get editionURLinAdmin(): string {
    return this._config.API_ENDPOINT + '/admin/fieldmapping/';
  }
}
