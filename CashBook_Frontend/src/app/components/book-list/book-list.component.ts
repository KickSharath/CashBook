import { Component, EventEmitter, Input, OnInit, Output, SimpleChanges } from '@angular/core';
import { CashbookService } from '../../core/services/cashbook.service';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { bookmarkSVG } from '../../shared/utils/svg'

@Component({
  selector: 'app-book-list',
  templateUrl: 'book-list.component.html',
  styleUrls: ['book-list.component.css']
})
export class BookListComponent implements OnInit {
  @Input() receivedData:any;
  @Output() sentData = new EventEmitter<any>();

  bookmarkSVG!: SafeHtml;

  bookList: any[] = [];
  newBookName = '';
  selectedBook: any | null = null;
  uploadFile: File | null = null;
  isLoading: any = {loadBookFlag: false}

  constructor(private cashbookService: CashbookService, private sanitizer: DomSanitizer) {
    this.getSVG()
  }

  ngOnInit() { 
    this.isLoading.loadBookFlag = true;
    this.loadBooks();
  }

  ngOnChanges(changes: SimpleChanges): void{
    console.log('Book List: ',this.receivedData)
    if(this.receivedData?.action == 'refreshData'){
      this.loadBooks();
    }
  }

  loadBooks() {
    this.cashbookService.getBooks(this.receivedData?.user_data?.user_id).subscribe({
      next: res =>{
        this.bookList = res
        this.isLoading.loadBookFlag = false;
      },
      error: err => console.error(err)
    });
  }

  actionBook(event:any, action:string, book:any){
    event.stopPropagation(); 
    switch(action){
      case 'viewBook': {
        this.selectedBook = book
        this.SentData(action)
        break;
      } 
      case 'EditBook': {
        this.selectedBook = book
        this.SentData(action)
        break;
      } 
      case 'deleteBook': {
        if (!confirm(`Delete book "${book?.book_name}"?`)) return;
        this.cashbookService.deleteBook(book?.book_id).subscribe({
          next: () => { 
            if (this.selectedBook === book) this.selectedBook = null; 
            this.loadBooks(); 
          },
          error: err => alert(err.error.detail)
        });
        break;
      } 
      default: {
        break;
      }
    }
  }

  getSVG(){
    this.bookmarkSVG = this.sanitizer.bypassSecurityTrustHtml(bookmarkSVG);
  }

  SentData(data: any){
    const isSendData = ['EditBook', 'viewBook']
    const book = isSendData.includes(data)? this.selectedBook:null
    const send = {
      action: data,
      data: book
    }
    this.sentData.emit(send)
  }
  
}
