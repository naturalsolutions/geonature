import { Component, OnInit } from "@angular/core";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatIconModule } from "@angular/material/icon";
import { ActivatedRoute, Router, RouterModule } from "@angular/router";
import { AuthService, User } from "@geonature/components/auth/auth.service";
import { ModuleService } from "@geonature/services/module.service";
import { NotificationDataService } from "@geonature/components/notification/notification-data.service";
import { ConfigService } from "@geonature/services/config.service";
import { AppSideNavService } from "../app-sidenav-service";
import { MatTooltipModule } from "@angular/material/tooltip";
import { GN2CommonModule } from "@geonature_common/GN2Common.module";
import { Subscription } from "rxjs";
import { TranslateService } from "@ngx-translate/core";

@Component({
  standalone: true,
  selector: 'pnx-app-toolbar',
  templateUrl: './app-toolbar.component.html',
  styleUrls: ['./app-toolbar.component.scss'],
  imports: [GN2CommonModule, MatToolbarModule, MatIconModule, MatTooltipModule, RouterModule],
})
export class AppToolbarComponent implements OnInit {
  private subscription: Subscription;
  public moduleName = 'Accueil';
  public moduleUrl: string;
  public currentUser: User;
  public currentDocUrl: string;
  public locale: string;

  public notificationNumber: number;
  public useLocalProvider: boolean; // Indicate if the user is logged in using a non local provider

  constructor(
    public authService: AuthService,
    private _moduleService: ModuleService,
    private _notificationDataService: NotificationDataService,
    public config: ConfigService,
    private _sideNavService: AppSideNavService,
    private _router: Router,
    private _activatedRoute: ActivatedRoute,
    private _translateService: TranslateService
  ) {}

  ngOnInit() {
    // Subscribe to router eventfrontend/src/app/components/nav-home
    this.onModuleChange();

    // Put the user name in navbar
    this.currentUser = this.authService.getCurrentUser();
    this.useLocalProvider = this.authService.canBeLoggedWithLocalProvider();
  }

  private onModuleChange() {
    this._moduleService.currentModule$.subscribe((module) => {
      if (!module) {
        // If in Home Page
        module = this._sideNavService.getHomeItem();
        module.module_doc_url = this._moduleService.geoNatureModule.module_doc_url;
      }
      this.moduleName = module.module_label;
      this.moduleUrl = module.module_url;
      if (module.module_doc_url) {
        this.currentDocUrl = module.module_doc_url;
      }
    });
    if (this.config.NOTIFICATIONS_ENABLED == true) {
      // Update notification count to display in badge
      this.updateNotificationCount();
    }
  }

  closeSideBar() {
    this._sideNavService.toggleSideNav();
    if (this.config.NOTIFICATIONS_ENABLED == true) {
      // Update notification count to display in badge
      this.updateNotificationCount();
    }
  }

  private updateNotificationCount() {
    this._notificationDataService.getNotificationsNumber().subscribe((count) => {
      this.notificationNumber = count;
    });
  }

  openNotification() {
    this.updateNotificationCount();
    this._router.navigate(['/notification']);
  }

  private extractLocaleFromUrl() {
    this.subscription = this._activatedRoute.queryParams.subscribe((param: any) => {
      const locale = param['locale'];
      if (locale !== undefined) {
        this.defineLanguage(locale);
      } else {
        this.locale = this._translateService.getDefaultLang();
      }
    });
  }

  changeLanguage(lang) {
    this.defineLanguage(lang);
    const prev = this._router.url;
    this._router.navigate(['/']).then((data) => {
      this._router.navigate([prev]);
    });
  }

  private defineLanguage(lang) {
    this.locale = lang;
    this._translateService.use(lang);
    this._translateService.setDefaultLang(lang);
  }

  ngOnDestroy() {
    // Prevent memory leak by unsubscribing
    this.subscription.unsubscribe();
  }
}
