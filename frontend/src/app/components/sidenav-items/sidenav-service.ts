import { Injectable } from '@angular/core';
import { MatSidenav } from '@angular/material/sidenav';
import { Module } from '@geonature/models/module.model';
import { Subject } from 'rxjs';

@Injectable()
export class SideNavService {
  sidenav: MatSidenav;
  // collapsed, the sidenav stays visible as an icon rail
  expanded = false;
  private _module = new Subject<any>();
  public currentModule: any;
  gettingCurrentModule = this._module.asObservable();
  // List of the apps
  public modules: Array<any>;
  public home_page;
  public exportModule;

  setSideNav(sidenav: MatSidenav) {
    this.sidenav = sidenav;
  }

  setHome(sidenav: MatSidenav) {
    this.open();
  }

  open() {
    this.expanded = true;
  }

  close() {
    this.expanded = false;
  }

  getCurrentApp() {
    return this.currentModule;
  }

  getHomeItem(): Module {
    return {
      module_url: '/',
      module_label: 'Home',
      module_picto: 'fa-home',
      id_module: 1,
      module_path: '/geonature',
    };
  }

  toggleSideNav() {
    this.expanded = !this.expanded;
  }
}
