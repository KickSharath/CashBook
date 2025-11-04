import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AUTH_API } from '../../constants/api-endpoints';

export interface User {
  user_id?: string;
  user_name: string;
  email: string;
  password?: string;
}

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private http: HttpClient) { }

  register(user: User): Observable<any> {
    return this.http.post(AUTH_API.REGISTER, user);
  }

  login(email: string, password: string): Observable<any> {
    return this.http.post(AUTH_API.LOGIN, { email, password });
  }

  getUser(user_id: string): Observable<any> {
    return this.http.get(`${AUTH_API.GETUSER}/${user_id}`);
  }
}
