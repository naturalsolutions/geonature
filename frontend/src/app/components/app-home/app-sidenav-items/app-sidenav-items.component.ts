import { Component, OnInit } from '@angular/core';
import { ConfigService } from '@geonature/services/config.service';
import { ModuleService } from '@geonature/services/module.service';
import { AppSideNavService } from '../app-sidenav-service'
import { MatCardModule } from '@angular/material/card';
import { MatListModule } from '@angular/material/list';
import { RouterModule } from '@librairies/@angular/router';
@Component({
  standalone: true,
  selector: 'pnx-app-sidenav-items',
  templateUrl: './app-sidenav-items.component.html',
  styleUrls: ['./app-sidenav-items.component.scss'],
  imports: [MatCardModule, MatListModule, RouterModule],
})
export class AppSidenavItemsComponent implements OnInit {
  public nav = [{}];
  public version = null;
  public home_page: any;
  public exportModule: any;

  constructor(
    public moduleService: ModuleService,
    public _sidenavService: AppSideNavService,
    public config: ConfigService
  ) {
    this.version = this.config.GEONATURE_VERSION;
  }

  ngOnInit() {
    this.home_page = this._sidenavService.getHomeItem();
  }

  setHome() {
    this.moduleService.currentModule$.next(null);
  }
}
