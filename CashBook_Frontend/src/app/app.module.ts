import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { BookListComponent } from './components/book-list/book-list.component';
import { AppComponent } from './app.component';
import { HomeComponent } from './components/home/home.component';
import { ModalPopupComponent } from './shared/components/modal-popup/modal-popup.component';
import { ViewBookComponent } from './components/view-book/view-book.component';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import {MatTableModule} from '@angular/material/table';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { AppRoutingModule } from './app-routing.module';
import { LoaderComponent } from './shared/components/loader/loader.component';
import { SharedModule } from './shared/shared.module';
import { LoaderInterceptor } from './core/interceptors/loader.interceptor';
import { MiniCalculatorComponent } from './shared/components/mini-calculator/mini-calculator.component';

@NgModule({
  declarations: [
    AppComponent, 
    HomeComponent, 
    BookListComponent, 
    ViewBookComponent , 
    ModalPopupComponent,
    LoginComponent,
    RegisterComponent,
    MiniCalculatorComponent
  ],
  imports: [
    BrowserModule, 
    FormsModule, 
    HttpClientModule, 
    MatTableModule,
    AppRoutingModule,
    SharedModule
  ],
  bootstrap: [AppComponent],
  providers: [
    provideAnimationsAsync(),
    {
      provide: HTTP_INTERCEPTORS,
      useClass: LoaderInterceptor,
      multi: true
    }
  ],
})
export class AppModule {}
