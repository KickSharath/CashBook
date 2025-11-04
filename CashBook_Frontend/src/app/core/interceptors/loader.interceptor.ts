import { Injectable } from '@angular/core';
import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { LoaderService } from '../services/loader.service';

@Injectable()
export class LoaderInterceptor implements HttpInterceptor {
  constructor(private loaderService: LoaderService) { }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const shouldSkipHeader = req.headers.has('skip-loader');
    const shouldSkip = shouldSkipHeader;

    if (!shouldSkip) {
      this.loaderService.show();
    }

    return next.handle(req).pipe(
      finalize(() => {
        if (!shouldSkip) {
          this.loaderService.hide();
        }
      })
    );
  }
}
