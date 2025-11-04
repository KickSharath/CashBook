export const BASE_URL = 'http://127.0.0.1:8000/api';

export const CASHBOOK_API = {
  // BASE: `${BASE_URL}/cashbook`,

  BOOKS: `${BASE_URL}/cashbook/books`,
  BOOK_BY_ID: (bookId: string) => `${BASE_URL}/cashbook/books/${bookId}`,
  BOOK_UPLOAD: `${BASE_URL}/cashbook/books/upload`,

  TRANSACTIONS_BY_BOOK: (bookId: string) => `${BASE_URL}/cashbook/transactions/${bookId}`,
  ADD_TRANSACTION: `${BASE_URL}/cashbook/add_transaction`,
  TRANSACTION_BY_ID: (transactionId: string) => `${BASE_URL}/cashbook/transactions/${transactionId}`,
  EXPORT: (bookId: string, fileType: string) =>
    `${BASE_URL}/cashbook/books/${bookId}/export?file_type=${fileType}`,
};

export const AUTH_API = {
    // BASE: `${BASE_URL}/auth`,

    REGISTER: `${BASE_URL}/auth/register`,
    LOGIN: `${BASE_URL}/auth/login`,
    GETUSER: `${BASE_URL}/auth/get-user`
}