import { Component, OnInit, Input, EventEmitter, Output, SimpleChanges } from '@angular/core';
import { CashbookService } from '../../core/services/cashbook.service';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { equalCircleSVG } from '../../shared/utils/svg';

@Component({
  selector: 'app-view-book',
  templateUrl: 'view-book.component.html',
  styleUrls: ['view-book.component.css']
})
export class ViewBookComponent implements OnInit {
  @Input() receivedData: any;
  @Output() sentData = new EventEmitter<any>();

  equalCircleSVG!: SafeHtml;
  transactionsRespones: any;
  displayedColumns: string[] = ['dataTime', 'remark', 'category', 'mode', 'amount', 'balance', 'actionbtn'];
  isDownlaoding: any = { flag: false, type: [] }
  
  constructor(private cashbookService: CashbookService, private sanitizer: DomSanitizer) {
    this.getSVG()
  }

  ngOnInit() {
    if (this.receivedData) this.loadTransactions();
  }

  ngOnChanges(changes: SimpleChanges): void{
      if(this.receivedData?.action == 'refreshData'){
        this.loadTransactions();
      }
    }


  loadTransactions() {
    this.cashbookService.getTransactions(this.receivedData?.data?.book_id).subscribe({
      next: transactions => {
        this.transactionsRespones = transactions;
      },
      error: err => console.error(err)
    });
  }

  actionTransaction(action: string, trans:any) {
    console.log(action, trans)
    switch(action){
      case 'EditTransaction': {
        this.SentData(action, trans);
        break;
      }
      case 'delete': {
        if (!confirm(`Delete book "${trans?.transaction_amount}"?`)) return;
        this.cashbookService.deleteTransaction(trans.transaction_id).subscribe({
          next:(data) => { 
          this.loadTransactions();
          },
          error: (err) => {
            console.error(err)
          }
        })
        break;
      }
      default: {
        break;
      }
    }
  }

  getSVG(){
    this.equalCircleSVG = this.sanitizer.bypassSecurityTrustHtml(equalCircleSVG);
  }

  SentData(data: any, trans?:any){
    const isSendData = ['AddTransactionIn', 'AddTransactionOut', 'EditTransaction']
    const book = isSendData.includes(data)? this.receivedData?.data:null
    let send:any = {
      action: data,
      data: book
    }
    if(data == 'EditTransaction') send.transactionData = trans
    this.sentData.emit(send)
  }

  downloadFile(bookId: string, fileType: 'csv' | 'xlsx' | 'pdf') {
    this.isDownlaoding.flag = true
    this.isDownlaoding.type.push(fileType)
    this.cashbookService.downloadTransactions(bookId, fileType).subscribe(
      (blob) => {
        const fileName = `book_transactions.${fileType}`;
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = fileName;
        link.click();
        window.URL.revokeObjectURL(link.href);
        setTimeout(() => {
          this.isDownlaoding.flag = false
          this.isDownlaoding.type.pop(fileType)
        });
      },
      (error) => {
        console.error('Download failed', error);
        alert('Failed to download file.');
      }
    );
  }
}
