import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { UserService } from '../../core/services/user.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html'
})
export class LoginComponent {
  email = '';
  password = '';
  error = '';

  constructor(private userService: UserService, private router: Router) { }

  login() {
    this.userService.login(this.email, this.password).subscribe({
      next: (res: any) => {
        localStorage.setItem('user', JSON.stringify(res.user));
        this.router.navigate(['/']);
      },
      error: (err) => {
        this.error = err.error.detail || 'Login failed';
      }
    });
  }

  goToRegister() {
    this.router.navigate(['/register']);
  }
}
