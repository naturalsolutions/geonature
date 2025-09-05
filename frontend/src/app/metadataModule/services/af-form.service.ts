import { Injectable } from '@angular/core';
import {
  UntypedFormGroup,
  UntypedFormArray,
  UntypedFormBuilder,
  Validators,
  UntypedFormControl,
} from '@angular/forms';
import { isEqual } from 'lodash';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap, filter, switchMap, map, distinctUntilChanged } from 'rxjs/operators';
import { ActorFormService } from './actor-form.service';
import { FormService } from '@geonature_common/form/form.service';
import { MapService } from '@geonature_common/map/map.service';

@Injectable()
export class AcquisitionFrameworkFormService {
  public form: UntypedFormGroup;
  public acquisition_framework: BehaviorSubject<any> = new BehaviorSubject(null);

  private _geometry: UntypedFormControl;
  public geojson: BehaviorSubject<any> = new BehaviorSubject(null);
  public markerCoordinates;
  public leafletDrawGeoJson;

  get geometry() {
    return this._geometry;
  }

  constructor(
    private fb: UntypedFormBuilder,
    private actorFormS: ActorFormService,
    private formS: FormService,
    private _mapService: MapService
  ) {
    this.initForm();
    this.setObservables();
  }

  private get initialValues(): Observable<any> {
    return this.actorFormS._role_types.asObservable().pipe(
      map((role_types: any[]): number => {
        //recherche du role "Contact principal" (cd_nomenclature = "1") pour l'attribuer par defaut.
        const role_type = role_types.find((role_type) => role_type.cd_nomenclature == '1');
        return role_type ? role_type.id_nomenclature : null;
      }),
      filter((id_nomenclature: number) => id_nomenclature !== null),
      map((id_nomenclature: number): any => {
        //formate les donnés par défauts envoyées au formulaire
        return {
          is_parent: false,
          cor_objectifs: [],
          cor_volets_sinp: [],
          cor_territories: [],
          cor_af_actor: [{ id_nomenclature_actor_role: id_nomenclature }],
        };
      })
    );
  }

  initForm(): void {
    this._geometry = new UntypedFormControl(null);
    //FORM
    this.form = this.fb.group({
      acquisition_framework_name: [null, Validators.required],
      acquisition_framework_desc: [null, Validators.required],
      id_nomenclature_territorial_level: [null, Validators.required],
      territory_desc: null,
      keywords: null,
      id_nomenclature_financing_type: [null, Validators.required],
      target_description: null,
      ecologic_or_geologic_target: null,
      acquisition_framework_parent_id: null,
      is_parent: null,
      acquisition_framework_start_date: [null, Validators.required],
      acquisition_framework_end_date: null,
      cor_objectifs: [[], Validators.required],
      cor_volets_sinp: [[]],
      cor_territories: [[], Validators.required],
      cor_af_actor: this.fb.array(
        [],
        [
          this.actorFormS.mainContactRequired.bind(this.actorFormS),
          this.actorFormS.uniqueMainContactvalidator.bind(this.actorFormS),
          this.actorFormS.checkDoublonsValidator.bind(this.actorFormS),
        ]
      ),
      bibliographical_references: this.fb.array([]),
      geometry: this._geometry,
    });

    this.form.setValidators([
      this.formS.dateValidator(
        this.form.get('acquisition_framework_start_date'),
        this.form.get('acquisition_framework_end_date')
      ),
    ]);
  }

  setGeometryFromMap(geojson) {
    this.manageGeometryChange(geojson.geometry);
  }

  setGeometryFromAPI(geojson) {
    this.manageGeometryChange(geojson);
    if (geojson.type == 'Point') {
      this.markerCoordinates = geojson.coordinates;
      this.leafletDrawGeoJson = geojson;
    } else {
      this.leafletDrawGeoJson = geojson;
    }
  }

  manageGeometryChange(geojson) {
    console.log(geojson);

    if (!isEqual(geojson, this._geometry.value)) {
      this._geometry.setValue(geojson);
      this._geometry.markAsDirty();
      //this.occtaxFormService.disabled = false;
    }
  }

  /**
   * Initialise les observables pour la mise en place des actions automatiques
   **/
  private setObservables() {
    //Observable de this.dataset pour adapter le formulaire selon la donnée
    this.acquisition_framework
      .asObservable()
      .pipe(
        tap(() => this.reset()),
        switchMap((af) =>
          af !== null ? this.acquisition_framework.asObservable() : this.initialValues
        ),
        map((value) => {
          if (value.cor_af_actor) {
            if (this.actorFormS.nbMainContact(value.cor_af_actor) == 0) {
              value.cor_af_actor.push({
                id_nomenclature_actor_role: this.actorFormS.getIDRoleTypeByCdNomenclature('1'),
              });
            }
            value.cor_af_actor.forEach((actor) => {
              this.addActor(this.actors, actor);
            });
          }
          if (value.bibliographical_references) {
            value.bibliographical_references.forEach((e) => {
              this.addBibliographicalReferences();
            });
          }
          return {
            ...value,
            acquisition_framework_name: 'a',
            acquisition_framework_desc: 'a',
            id_nomenclature_territorial_level: 358,
            id_nomenclature_financing_type: 385,
            acquisition_framework_start_date: { year: 2025, month: 9, day: 5 },
            cor_af_actor: [
              {
                id_nomenclature_actor_role: 359,
                id_organism: 2,
                id_role: null,
                id_cda: null,
                id_cafa: null,
              },
            ],
            cor_territories: [
              {
                active: true,
                cd_nomenclature: 'METROP',
                definition_default: 'Métropole',
                definition_fr: 'Métropole',
                hierarchy: '110.001',
                id_broader: 0,
                id_nomenclature: 366,
                id_type: 110,
                label_default: 'Métropole',
                label_fr: 'Métropole',
                mnemonique: 'Métropole',
                source: 'SINP',
                statut: 'Validé',
              },
            ],
            cor_objectifs: [
              {
                active: true,
                cd_nomenclature: '9',
                definition_default:
                  "L'acquisition des données d'occurrence est réalisée avec un dispositif de collecte comprenant une répétition de l'acquisition au cours du temps. La démarche permet une comparaison d'un état entre différentes périodes pour un ou plusieurs objets de biodiversité. Elle est mise en place en lien avec une thématique prédéterminée (biologie de la conservation, changements globaux, …).",
                definition_fr:
                  "L'acquisition des données d'occurrence est réalisée avec un dispositif de collecte comprenant une répétition de l'acquisition au cours du temps. La démarche permet une comparaison d'un état entre différentes périodes pour un ou plusieurs objets de biodiversité. Elle est mise en place en lien avec une thématique prédéterminée (biologie de la conservation, changements globaux, …).",
                hierarchy: '108.009',
                id_broader: 0,
                id_nomenclature: 517,
                id_type: 108,
                label_default: 'Suivi/surveillance dans le temps',
                label_fr: 'Suivi/surveillance dans le temps',
                mnemonique: 'SuivSurv',
                source: 'SINP',
                statut: 'Validé',
              },
            ],
          };
        })
      )
      .subscribe((value: any) => {
        console.log('patchValue', value);

        this.form.patchValue(value);
      });

    //gère lactivation/désactivation de la zone de saisie du framework Parent
    this.form.get('is_parent').valueChanges.subscribe((value: boolean) => {
      if (value) {
        this.form.get('acquisition_framework_parent_id').disable();
      } else {
        this.form.get('acquisition_framework_parent_id').enable();
      }
    });

    this._mapService.gettingGeojson$
      .pipe(
        distinctUntilChanged(),
        filter((geojson) => geojson !== null)
      )
      .subscribe((geojson) => {
        this.setGeometryFromMap(geojson);
      });
  }

  get actors(): UntypedFormArray {
    return this.form.get('cor_af_actor') as UntypedFormArray;
  }

  //ajoute un acteur au formulaire, par défaut un acteur vide est ajouté
  addActor(formArray, value: any = null): void {
    const actorForm = this.actorFormS.createForm();
    if (value) {
      actorForm.patchValue(value);
    }
    formArray.push(actorForm);
  }

  removeActor(formArray: UntypedFormArray, i: number): void {
    formArray.removeAt(i);
  }

  get bibliographicalReferences(): UntypedFormArray {
    return this.form.get('bibliographical_references') as UntypedFormArray;
  }

  //ajoute un acteur au formulaire, par défaut un acteur vide est ajouté
  addBibliographicalReferences(): void {
    const biblioRefForm = this.fb.group({
      id_bibliographic_reference: null,
      publication_url: null,
      publication_reference: [null, Validators.required],
    });
    this.bibliographicalReferences.push(biblioRefForm);
  }

  removeBibliographicalReferences(i: number): void {
    this.bibliographicalReferences.removeAt(i);
  }

  //retourne true sur l'acteur est contact principal
  isMainContact(actorForm) {
    return (
      actorForm.get('id_nomenclature_actor_role').value ==
      this.actorFormS.getIDRoleTypeByCdNomenclature('1')
    );
  }

  reset() {
    this.clearFormArray(this.form.get('cor_af_actor') as UntypedFormArray);
    this.form.reset();
  }

  private clearFormArray(formArray: UntypedFormArray) {
    while (formArray.length !== 0) {
      formArray.removeAt(0);
    }
  }
}
