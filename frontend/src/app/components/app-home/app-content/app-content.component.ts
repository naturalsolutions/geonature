import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  standalone: true,
  selector: 'pnx-app-content',
  templateUrl: './app-content.component.html',
  styleUrls: ['./app-content.component.scss'],
  imports: [RouterOutlet]
})
export class AppContentComponent {
}


