import { ActivatedRoute, Router } from '@angular/router';
import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { MatSidenav, MatSidenavModule } from '@angular/material/sidenav';

import { Subscription } from 'rxjs';
import { TranslateService } from '@ngx-translate/core';

import { AuthService, User } from '../auth/auth.service';
import { ModuleService } from '../../services/module.service';
import { NotificationDataService } from '@geonature/components/notification/notification-data.service';
import { ConfigService } from '@geonature/services/config.service';

import { AppSidenavComponent } from './app-sidenav/app-sidenav.component';
import { AppSideNavService } from './app-sidenav-service';
import { AppToolbarComponent } from './app-toolbar/app-toolbar.component';
import { AppContentComponent } from './app-content/app-content.component';
@Component({
  standalone: true,
  selector: 'pnx-app-home',
  templateUrl: './app-home.component.html',
  styleUrls: ['./app-home.component.scss'],
  imports: [AppSidenavComponent, AppToolbarComponent, AppContentComponent, MatSidenavModule],
  providers: [AppSideNavService]
})
export class NavHomeComponent implements OnInit {
  @ViewChild('sidenav', { static: true }) public sidenav: MatSidenav;

  constructor(
    public sideNavService: AppSideNavService,
  ) {}

  ngOnInit() {
    // Init the sidenav instance in sidebar service
    this.sideNavService.setSideNav(this.sidenav);
  }
}
