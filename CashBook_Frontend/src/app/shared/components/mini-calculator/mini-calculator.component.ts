import { Component, Input, OnChanges } from '@angular/core';

@Component({
  selector: 'app-mini-calculator',
  templateUrl: './mini-calculator.component.html',
  styleUrls: ['./mini-calculator.component.css']
})
export class MiniCalculatorComponent implements OnChanges {
  @Input() balances: { balance: number }[] = [];

  defaultBalances: { balance: number }[] = [];
  currentBalances: { balance: number, isUser?: boolean }[] = [];

  total: number = 0;
  expression: string = '';
  newValue: number | null = null;

  ngOnChanges() {
    this.defaultBalances = this.balances.filter(b => b.balance != 0).map(b => ({ balance: b.balance }));
    this.currentBalances = this.defaultBalances.map(b => ({ ...b, isUser: false }));
    this.recalculate();
  }

  addValue() {
    if (this.newValue !== null && !isNaN(this.newValue)) {
      this.currentBalances.push({ balance: this.newValue, isUser: true });
      this.newValue = null;
      this.recalculate();
    }
  }

  removeValue(index: number) {
    this.currentBalances.splice(index, 1);
    this.recalculate();
  }

  reAddDefault(bal: { balance: number }) {
    if (!this.currentBalances.some(b => b.balance === bal.balance && !b.isUser)) {
      this.currentBalances.push({ ...bal, isUser: false });
      this.recalculate();
    }
  }

  recalculate() {
    const nums = this.currentBalances.map(b => Number(b.balance) || 0);
    this.total = nums.reduce((sum, val) => sum + val, 0);
    this.expression = nums.join(' + ');
  }

  get removedDefaults() {
    return this.defaultBalances.filter(d =>
      !this.currentBalances.some(c => c.balance === d.balance && !c.isUser)
    );
  }
}
