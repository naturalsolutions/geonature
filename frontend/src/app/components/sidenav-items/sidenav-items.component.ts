import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '../../services/module.service';
import { SideNavService } from './sidenav-service';
import { ReferentialData, UtilsService } from '@geonature/services/utils.service';
import { Module } from '@geonature/models/module.model';
import { Observable } from 'rxjs';

@Component({
  selector: 'pnx-sidenav-items',
  templateUrl: './sidenav-items.component.html',
  styleUrls: ['./sidenav-items.component.scss'],
})
export class SidenavItemsComponent implements OnInit {
  public nav = [{}];
  public version = null;
  public home_page: any;
  public ref_data: ReferentialData[];
  public isRefVersionLoaded = false;

  constructor(
    public moduleService: ModuleService,
    public _sidenavService: SideNavService,
    public utilsService: UtilsService,
    public config: ConfigService,
    private _router: Router
  ) {
    this.version = this.config.GEONATURE_VERSION;
  }

  ngOnInit() {
    this.home_page = this._sidenavService.getHomeItem();
  }

  setHome() {
    this.moduleService.currentModule$.next(null);
  }

  // in-app links declared as external urls (e.g. monitoring sub-modules) carry a hash route
  isCurrentExternal(module: Module): boolean {
    const route = module.module_external_url?.split('#')[1];
    return !!route && this._router.url.startsWith(route);
  }

  getModulesVersionTooltip(): Module[] {
    return this.moduleService.getModules();
  }

  onMenuOpened(): void {
    if (!this.isRefVersionLoaded) {
      this.utilsService.getRefVersion().subscribe((data: ReferentialData[]) => {
        this.ref_data = data;
        this.isRefVersionLoaded = true;
      });
    }
  }
}
