import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { CASHBOOK_API } from '../../constants/api-endpoints';


@Injectable({ providedIn: 'root' })
export class CashbookService {
  private skipLoaderHeader = new HttpHeaders({ 'skip-loader': 'true' });

  constructor(private http: HttpClient) {}

  getBooks(userId: string): Observable<any> {
    return this.http.get(`${CASHBOOK_API.BOOKS}/${userId}`,{ headers: this.skipLoaderHeader });
  }

  createBook(payload: any): Observable<any> {
    return this.http.post(CASHBOOK_API.BOOKS, payload);
  }

  editBook(book_id: string, newName: string): Observable<any> {
    return this.http.put(`${CASHBOOK_API.BOOK_BY_ID(book_id)}?new_name=${newName}`, {});
  }

  deleteBook(book_id: string): Observable<any> {
    return this.http.delete(CASHBOOK_API.BOOK_BY_ID(book_id));
  }

  getTransactions(book_id: string): Observable<any> {
    return this.http.get(CASHBOOK_API.TRANSACTIONS_BY_BOOK(book_id));
  }

  addTransaction(payload: any): Observable<any> {
    return this.http.post(CASHBOOK_API.ADD_TRANSACTION, payload);
  }

  updateTransaction(transaction_id: string, payload: any): Observable<any> {
    return this.http.put(CASHBOOK_API.TRANSACTION_BY_ID(transaction_id), payload);
  }

  deleteTransaction(transaction_id: string): Observable<any> {
    return this.http.delete(CASHBOOK_API.TRANSACTION_BY_ID(transaction_id));
  }

  uploadFile(userId: string, bookName: string, file: File): Observable<any> {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('book_name', bookName);
    formData.append('file', file, file.name);

    return this.http.post(CASHBOOK_API.BOOK_UPLOAD, formData)
  }

  downloadTransactions(bookId: string, fileType: 'csv' | 'xlsx' | 'pdf') {
    return this.http.get(CASHBOOK_API.EXPORT(bookId, fileType), { responseType: 'blob', headers: this.skipLoaderHeader });
  }
}
