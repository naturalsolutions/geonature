import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '@geonature/components/auth/auth.service';

/**
 * Route racine : redirige immédiatement sans rien afficher.
 * - utilisateur connecté  -> /synthese
 * - visiteur anonyme       -> /login (formulaire + bouton "Accès public")
 *
 * Placé hors du shell NavHomeComponent (donc sans AuthGuard sur canActivateChild),
 * pour éviter que le 401 anonyme n'annule la navigation avant la redirection.
 */
@Component({
  selector: 'pnx-home-redirect',
  template: '',
})
export class HomeRedirectComponent implements OnInit {
  constructor(
    private _router: Router,
    private _auth: AuthService
  ) {}

  ngOnInit() {
    this._router.navigateByUrl(this._auth.isLoggedIn() ? '/synthese' : '/login');
  }
}
