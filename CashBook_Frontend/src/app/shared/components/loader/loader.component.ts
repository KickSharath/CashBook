import { Component } from '@angular/core';
import { LoaderService } from '../../../core/services/loader.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-loader',
  templateUrl: './loader.component.html',
  styleUrls: ['./loader.component.css']
})
export class LoaderComponent {
  loading$: Observable<boolean>;
  constructor(private loaderService: LoaderService) {
    this.loading$ = loaderService.loading$;
  }
}
