import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { User, UserService } from '../../core/services/user.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html'
})
export class RegisterComponent {
  user_name = '';
  email = '';
  password = '';
  error = '';

  constructor(private userService: UserService, private router: Router) { }

  register() {
    const user: User = {
      user_name: this.user_name,
      email: this.email,
      password: this.password
    };
    this.userService.register(user).subscribe({
      next: () => {
        alert('Registered successfully. Please login.');
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.error = err.error.detail || 'Registration failed';
      }
    });
  }

  goToLogin() {
    this.router.navigate(['/login']);
  }
}
