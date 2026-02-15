import { Component, EventEmitter, Input, OnInit, Output, SimpleChanges, ViewChild } from '@angular/core';
import { CashbookService } from '../../core/services/cashbook.service';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { bookmarkSVG } from '../../shared/utils/svg'
import { TooltipDirective } from '../../shared/directives/tooltip.directive';
import { ToastService } from '../../core/services/toast.service';

@Component({
  selector: 'app-book-list',
  templateUrl: 'book-list.component.html',
  styleUrls: ['book-list.component.css']
})
export class BookListComponent implements OnInit {
  @Input() receivedData:any;
  @Output() sentData = new EventEmitter<any>();
  @ViewChild(TooltipDirective) tooltipDirective!: TooltipDirective;

  bookmarkSVG!: SafeHtml;

  bookList: any[] = [];
  newBookName = '';
  selectedBook: any | null = null;
  uploadFile: File | null = null;
  isLoading: any = {loadBookFlag: false}
  currentExpression: any = "Getting Expression..."

  constructor(private cashbookService: CashbookService, private sanitizer: DomSanitizer, private toastService: ToastService) {
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

  getTotalExpression(event:any){
    this.currentExpression = event
  }

  actionButton(type: string){
    const messageService =['Telegram']

    let text = '';

    if(type === 'copy'){
      text = this.bookList.map(d=> {
        return `• ${d.book_name}: ${d.balance}`
      }).join('\n')

      text = `${text}\n\n\n${this.currentExpression}`

      this.copyToBoard(text)
    }else if(messageService.includes(type)){
      text = this.bookList.map(d => {
        return `• <b>${d.book_name}</b>: <tg-spoiler>${d.balance}</tg-spoiler>`;
      }).join('\n');

      text = `${text}\n\n<tg-spoiler>${this.currentExpression}</tg-spoiler>`;

      this.cashbookService.sendMessage(type, { message: text }).subscribe({
        next: (res: any) => {
          if (res && res.message && res.status_code) {
            if (res.status_code === 200) {
              this.toastService.success(res.message);
            } else {
              this.toastService.error(res.message);
            }
          } else {
            this.toastService.error('Failed to send message. Invalid response.');
          }
        },
        error: (err: any) => {
          console.error(err);
          this.toastService.error('Failed to send message. Please try again.');
        }
      })
    }
  }

  copyToBoard(text: string){    
    navigator.clipboard.writeText(text).then(() => {
      if (this.tooltipDirective) {
        this.tooltipDirective.showTemporaryTooltip('Copied!', '#28a745');
      }
    });
  }
  
}
