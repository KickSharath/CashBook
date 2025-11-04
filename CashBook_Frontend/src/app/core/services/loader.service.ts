import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LoaderService {
  private loadingSubject = new BehaviorSubject<boolean>(false);
  loading$ = this.loadingSubject.asObservable();

  private requestCount = 0;
  private minDisplayTime = 700;
  private loaderStartTime: number | null = null;
  private hideTimeout: any;

  show(): void {
    this.requestCount++;

    if (this.requestCount === 1) {
      this.loaderStartTime = new Date().getTime();
      this.loadingSubject.next(true);
    }
  }

  hide(): void {
    if (this.requestCount > 0) {
      this.requestCount--;
    }

    if (this.requestCount === 0 && this.loaderStartTime) {
      const elapsed = new Date().getTime() - this.loaderStartTime;

      if (elapsed < this.minDisplayTime) {
        this.hideTimeout = setTimeout(() => {
          this.loadingSubject.next(false);
          this.loaderStartTime = null;
        }, this.minDisplayTime - elapsed);
      } else {
        this.loadingSubject.next(false);
        this.loaderStartTime = null;
      }
    }
  }
}
