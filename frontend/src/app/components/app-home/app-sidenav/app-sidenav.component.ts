
import { Component } from '@angular/core';

import { AppSidenavItemsComponent } from './app-sidenav-items/app-sidenav-items.component';
import { MatSidenavModule } from '@angular/material/sidenav';
import { AppSideNavService } from '../app-sidenav-service';

@Component({
  standalone: true,
  selector: 'pnx-app-sidenav',
  templateUrl: './app-sidenav.component.html',
  styleUrls: ['./app-sidenav.component.scss'],
  imports: [AppSidenavItemsComponent, MatSidenavModule],
})
export class AppSidenavComponent {
  constructor(public sideNavService: AppSideNavService){}
}
