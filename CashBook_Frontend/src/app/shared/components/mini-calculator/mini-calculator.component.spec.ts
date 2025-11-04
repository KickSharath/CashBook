import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MiniCalculatorComponent } from './mini-calculator.component';

describe('MiniCalculatorComponent', () => {
  let component: MiniCalculatorComponent;
  let fixture: ComponentFixture<MiniCalculatorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MiniCalculatorComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(MiniCalculatorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
