import { Component, OnInit } from '@angular/core';
import { UntypedFormArray, UntypedFormGroup } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { NgbDateParserFormatter } from '@ng-bootstrap/ng-bootstrap';
import { of, Observable } from 'rxjs';
import { switchMap, tap, map } from 'rxjs/operators';

import { DataFormService } from '@geonature_common/form/data-form.service';
import { ConfigService } from '@geonature/services/config.service';
import { leafletDrawOption } from '@geonature_common/map/leaflet-draw.options';
import { MapService } from '@geonature_common/map/map.service';
import { CommonService } from '@geonature_common/service/common.service';
import { ActorFormService } from '../services/actor-form.service';
import { AcquisitionFrameworkFormService } from '../services/af-form.service';
import { MetadataService } from '../services/metadata.service';
import { MetadataDataService } from '../services/metadata-data.service';

@Component({
  selector: 'pnx-af-form',
  templateUrl: './af-form.component.html',
  styleUrls: ['../form.component.scss'],
  providers: [AcquisitionFrameworkFormService],
})
export class AfFormComponent implements OnInit {
  public form: UntypedFormGroup;
  //observable pour la liste déroulantes HTML des AF parents
  public acquisitionFrameworkParents: Observable<any>;

  public leafletDrawOptions: any;
  public firstFileLayerMessage = true;
  public coordinates = null;
  public geometry = null;
  public firstGeom = true;

  constructor(
    private _dfs: DataFormService,
    private _commonService: CommonService,
    private _route: ActivatedRoute,
    private _router: Router,
    private dateParser: NgbDateParserFormatter,
    public afFormS: AcquisitionFrameworkFormService,
    private actorFormS: ActorFormService,
    public metadataS: MetadataService,
    private metadataDataS: MetadataDataService,
    private _mapService: MapService,
    public config: ConfigService
  ) {}
  ngOnInit() {
    leafletDrawOption.draw.circle = false;
    leafletDrawOption.draw.rectangle = false;
    leafletDrawOption.draw.marker = false;
    leafletDrawOption.draw.polyline = true;
    leafletDrawOption.edit.remove = false;
    this.leafletDrawOptions = leafletDrawOption;

    // get the id from the route
    this._route.params
      .pipe(
        switchMap((params) => {
          return params['id']
            ? this.getAcquisitionFramework(params['id'], { exclude: ['t_datasets'] })
            : of(null);
        })
      )
      .subscribe((af) => this.afFormS.acquisition_framework.next(af));

    this.form = this.afFormS.form;

    // get acquisistion frameworks parent
    this._dfs.getAcquisitionFrameworks({ is_parent: 'true' }).subscribe((afParent) => {
      this.acquisitionFrameworkParents = afParent;
    });
  }

  ngAfterViewInit() {
    if (this._mapService.currentExtend) {
      this._mapService.map.setView(
        this._mapService.currentExtend.center,
        this._mapService.currentExtend.zoom
      );
    }
    let filelayerFeatures = this._mapService.fileLayerFeatureGroup.getLayers();
    // si il y a encore des filelayer -> on désactive le marker par defaut
    if (filelayerFeatures.length > 0) {
      this._mapService.setEditingMarker(false);
      this._mapService.fileLayerEditionMode = true;
    }

    filelayerFeatures.forEach((el) => {
      if ((el as any).getLayers()[0].options.color == 'red') {
        (el as any).setStyle({ color: 'green', opacity: 0.2 });
      }
    });
  }

  // display help toaster for filelayer
  infoMessageFileLayer() {
    if (this.firstFileLayerMessage) {
      this._commonService.translateToaster('info', 'Map.Messages.FileLayerInfo');
    }
    this.firstFileLayerMessage = false;
  }

  getAcquisitionFramework(id_af, param) {
    return this._dfs.getAcquisitionFramework(id_af, param).pipe(
      map((af: any) => {
        af.acquisition_framework_start_date = this.dateParser.parse(
          af.acquisition_framework_start_date
        );
        af.acquisition_framework_end_date = this.dateParser.parse(
          af.acquisition_framework_end_date
        );
        return af;
      })
    );
  }

  addContact(formArray: UntypedFormArray, mainContact: boolean) {
    let value = null;
    if (mainContact) {
      value = { id_nomenclature_actor_role: this.actorFormS.getIDRoleTypeByCdNomenclature('1') };
    }
    this.afFormS.addActor(formArray, value);
  }

  /* postAf() {
    console.log(this.form.value);  
  } */

  postAf() {
    if (!this.form.valid) return;

    let api: Observable<any>;

    const af = Object.assign(this.afFormS.acquisition_framework.getValue() || {}, this.form.value);

    af.acquisition_framework_start_date = this.dateParser.format(
      af.acquisition_framework_start_date
    );

    if (af.acquisition_framework_end_date) {
      af.acquisition_framework_end_date = this.dateParser.format(af.acquisition_framework_end_date);
    }
    //UPDATE
    if (this.afFormS.acquisition_framework.getValue() !== null) {
      //si modification on assigne les valeurs du formulaire au CA modifié
      api = this.metadataDataS.updateAF(af.id_acquisition_framework, af);
    } else {
      //si creation on envoie le contenu du formulaire
      console.log('af', af);

      api = this.metadataDataS.createAF(af);
    }

    //envoie de la requete au serveur
    api
      .pipe(
        tap(() => {
          this._commonService.translateToaster('success', 'MetaData.Messages.AFAdded');
          this.metadataS.getMetadata(); //rechargement de la liste de la page principale
        })
      )
      .subscribe(
        (acquisition_framework: any) => {
          console.log("res", acquisition_framework);
          
          /* this._router.navigate([
            '/metadata/af_detail',
            acquisition_framework.id_acquisition_framework,
          ]); */
        },
        (error) => {
          if (error.status === 403) {
            this._commonService.translateToaster('error', 'Errors.NotAllowed');
            this._router.navigate(['/metadata/']);
          }
        }
      );
  }
}
