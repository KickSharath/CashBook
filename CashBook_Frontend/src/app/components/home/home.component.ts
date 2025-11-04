import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  sentData: any = null
  user_data: any = null;
  // currentPage = 'viewPage'
  currentPage = 'homePage'

  constructor() { }

  ngOnInit(): void {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      this.user_data = JSON.parse(userStr);
    }
    this.sentData = {
      isPopup: false,
      user_data: this.user_data,
      action: null
    }
  }

  openPopup(action:any, data?:any){
    const actionList = ['AddNewBook', 'EditBook', 'AddTransactionIn', 'AddTransactionOut', 'EditTransaction', 'UploadFile']
    let isPopup = actionList.includes(action)? true: false;
    this.sentData = {
      isPopup: isPopup,
      user_data: this.user_data,
      action: action,
      data: data?data: null
    }
  }

  getData(receivedData:any){
    console.log('--->GetData: ', receivedData)
    if(receivedData && receivedData.action){
      if(receivedData?.action == 'viewBook'){
        this.currentPage = 'viewPage';
      }else if(receivedData?.action == 'viewHome'){
        this.currentPage = 'homePage';
      }
      let data = receivedData?.data? receivedData?.data: null;
      this.openPopup(receivedData.action, data)
      if(receivedData?.transactionData)  this.sentData.transactionData = receivedData?.transactionData;
    }
  }
}
