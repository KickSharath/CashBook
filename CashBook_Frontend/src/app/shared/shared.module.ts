import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoaderComponent } from './components/loader/loader.component';
import { TooltipDirective } from './directives/tooltip.directive';
import { ToastComponent } from './components/toast/toast.component';

@NgModule({
  declarations: [LoaderComponent, TooltipDirective, ToastComponent],
  imports: [CommonModule],
  exports: [LoaderComponent, TooltipDirective, ToastComponent]
})
export class SharedModule {}
