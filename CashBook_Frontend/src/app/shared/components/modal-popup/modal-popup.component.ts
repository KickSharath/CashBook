import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CashbookService } from '../../../core/services/cashbook.service';

@Component({
  selector: 'app-modal-popup',
  templateUrl: './modal-popup.component.html',
  styleUrl: './modal-popup.component.css'
})

export class ModalPopupComponent  {
  @Input() receivedData:any;
  @Output() sentData = new EventEmitter<any>();
  formData: any = {};
  fileAllowed: any = '.csv, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
  uploadFile: File | null = null;

  constructor(private cashbookService: CashbookService){}

  ngOnInit() {
    document.body.style.overflow = 'hidden';
    console.log('Modal Popup: ',this.receivedData)
    // const bookName = this.receivedData?.action == 'EditBook'? this.receivedData?.data?.book_name: '';
    // this.formData['book_name'] = bookName;
    if (this.receivedData?.action === 'EditBook') {
      this.formData.book_name = this.receivedData?.data?.book_name || '';
    }else if(this.receivedData?.action == 'AddTransactionIn' || this.receivedData?.action == 'AddTransactionOut'){
      let transactionType = ''
      if(this.receivedData?.action == 'AddTransactionIn') transactionType = 'in';
      if(this.receivedData?.action == 'AddTransactionOut') transactionType = 'out';
      this.formData.transaction_type = transactionType
    }else if(this.receivedData?.action == 'EditTransaction'){
      const data = this.receivedData?.transactionData;
      this.formData.transaction_amount = data?.transaction_amount || 0;
      this.formData.transaction_type = data?.transaction_type || '';
      this.formData.mode = data?.mode || '';
      this.formData.remark = data?.remark || '';
      this.formData.category = data?.category || '';
      this.formData.transaction_id = data?.transaction_id || '';
    }
  }

  SentData(action: any,data?:any){
    this.receivedData.isPopup = false;
    const send = {
      action: action,
      data: data
    }
    this.sentData.emit(send)
    document.body.style.overflow = '';
  }

  saveData(action:any){
    switch(action){
      case 'AddNewBook':
        this.createBook();
        break;
      case 'EditBook':
        this.editBook();
        break;
      case 'AddTransactionIn':
      case 'AddTransactionOut':
        this.addTransaction()
        break;
      case 'EditTransaction':
        this.editTransaction()
        break;
      case 'UploadFile':
        this.onUpload();
        break;
      default:
        break;
    }
  }

  // Books
  createBook() {
    if (!this.formData.book_name.trim() || !this.receivedData?.user_data?.user_id) return;

    const payload = { 
      user_id: this.receivedData?.user_data?.user_id, 
      book_name: this.formData.book_name, 
    };

    this.cashbookService.createBook(payload).subscribe({
      next: () => { 
        this.SentData('refreshData')
      },error: err => alert(err.error.detail)
    });
  }
  
  editBook() {
    if (!this.formData.book_name.trim() || !this.receivedData?.user_data?.user_id || !this.receivedData?.data) return;
    this.cashbookService.editBook(this.receivedData?.data?.book_id, this.formData.book_name.trim()).subscribe({
      next: () => {
        this.SentData('refreshData')
      },
      error: err => alert(err.error.detail)
    });
  }

  // Transactions
  addTransaction() {
    if(!this.formData?.transaction_amount || !this.formData?.transaction_type ) return;

    let payload = {
      "update_by": this.receivedData?.user_data?.user_id,
      "book_id": this.receivedData?.data?.book_id,
      "transaction_amount": this.formData.transaction_amount,
      "transaction_type": this.formData.transaction_type,
      "remark": this.formData.remark,
      "mode": this.formData.mode,
      "category": this.formData.category
    }

    this.cashbookService.addTransaction(payload).subscribe({
      next: (data:any) =>{
        this.SentData('refreshData', this.receivedData?.data)
      },
      error: (err:any) => {
        console.error(err)
      }
    })
  }

  editTransaction() {
    if(!this.formData?.transaction_amount || !this.formData?.transaction_type ) return;

    let payload = {
      "transaction_amount": this.formData.transaction_amount,
      "transaction_type": this.formData.transaction_type,
      "remark": this.formData.remark,
      "mode": this.formData.mode,
      "category": this.formData.category
    }

    this.cashbookService.updateTransaction(this.formData?.transaction_id, payload).subscribe({
      next: (data) => {
        this.SentData('refreshData', this.receivedData?.data)
      },
      error: (err) => {
        console.error(err)
      }
    })
  }

  // Upload File
  onFileSelected(event: any) {
    this.uploadFile = event.target.files[0] || null;
  }

  onUpload() {
    if (!this.receivedData?.user_data?.user_id || !this.formData.book_name || !this.uploadFile) {
      // this.error = 'Please fill all fields and select a file';
      console.error('Please fill all fields and select a file')
      return;
    }

    this.cashbookService.uploadFile(this.receivedData?.user_data?.user_id, this.formData.book_name, this.uploadFile)
      .subscribe({
        next: (data:any) => {
          this.SentData('refreshData')
        },
        error: (err:any) => {
          console.error(err)
        }
      });
  }
}
