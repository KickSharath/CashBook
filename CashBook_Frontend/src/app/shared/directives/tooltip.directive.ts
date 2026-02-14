import { Directive, ElementRef, HostListener, Input, OnInit, OnDestroy } from '@angular/core';

@Directive({
  selector: '[Tooltip]'
})
export class TooltipDirective implements OnInit, OnDestroy {
  @Input('Tooltip') message: string = '';
  @Input() tooltipPosition: 'top' | 'bottom' | 'left' | 'right' = 'top';
  @Input() tooltipBg: string = '#333';
  @Input() tooltipColor: string = '#fff';

  private tooltipElement: HTMLElement | null = null;
  private originalMessage: string = '';
  private hideTimeout: any = null;

  constructor(private el: ElementRef) {}

  ngOnInit() {
    this.el.nativeElement.style.position = 'relative';
    this.el.nativeElement.style.cursor = 'pointer';
    this.originalMessage = this.message;
  }

  @HostListener('mouseenter')
  onMouseEnter() {
    this.show();
  }

  @HostListener('mouseleave')
  onMouseLeave() {
    this.message = this.originalMessage;
    if (this.tooltipElement) {
      this.tooltipElement.textContent = this.originalMessage;
      this.tooltipElement.style.backgroundColor = this.tooltipBg;
    }
    if (this.hideTimeout) {
      clearTimeout(this.hideTimeout);
      this.hideTimeout = null;
    }
    this.hide();
  }

  private show() {
    if (!this.tooltipElement) {
      this.create();
    }
    if (this.tooltipElement) {
      this.tooltipElement.style.visibility = 'visible';
      this.tooltipElement.style.opacity = '1';
    }
  }

  private hide() {
    if (this.tooltipElement) {
      this.tooltipElement.style.visibility = 'hidden';
      this.tooltipElement.style.opacity = '0';
    }
  }

  showTemporaryTooltip(tempMessage: string, bgColor: string = '#28a745') {
    if (this.hideTimeout) {
      clearTimeout(this.hideTimeout);
      this.hideTimeout = null;
    }

    this.message = tempMessage;
    if (this.tooltipElement) {
      this.tooltipElement.textContent = tempMessage;
      this.tooltipElement.style.backgroundColor = bgColor;
      this.setPosition(this.tooltipElement);
    }

    this.show();
  }

  private create() {
    const tooltip = document.createElement('div');
    tooltip.className = `tooltip-directive tooltip-${this.tooltipPosition}`;
    tooltip.textContent = this.message;
    
    tooltip.style.position = 'absolute';
    tooltip.style.backgroundColor = this.tooltipBg;
    tooltip.style.color = this.tooltipColor;
    tooltip.style.padding = '8px 12px';
    tooltip.style.borderRadius = '4px';
    tooltip.style.fontSize = '12px';
    tooltip.style.whiteSpace = 'nowrap';
    tooltip.style.zIndex = '1000';
    tooltip.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.2)';
    tooltip.style.visibility = 'hidden';
    tooltip.style.opacity = '0';
    tooltip.style.transition = 'opacity 0.3s ease-in-out';
    
    this.setPosition(tooltip);
    
    this.el.nativeElement.appendChild(tooltip);
    this.tooltipElement = tooltip;
  }

  private setPosition(tooltip: HTMLElement) {
    setTimeout(() => {
      const hostWidth = this.el.nativeElement.offsetWidth;
      const hostHeight = this.el.nativeElement.offsetHeight;
      const tooltipWidth = tooltip.offsetWidth || tooltip.scrollWidth;
      const tooltipHeight = tooltip.offsetHeight || tooltip.scrollHeight;

      let top = 0;
      let left = 0;
      const offset = 10;

      switch (this.tooltipPosition) {
        case 'top':
          top = -tooltipHeight - offset;
          left = (hostWidth - tooltipWidth) / 2;
          break;
        case 'bottom':
          top = hostHeight + offset;
          left = (hostWidth - tooltipWidth) / 2;
          break;
        case 'left':
          top = (hostHeight - tooltipHeight) / 2;
          left = -tooltipWidth - offset;
          break;
        case 'right':
          top = (hostHeight - tooltipHeight) / 2;
          left = hostWidth + offset;
          break;
      }

      tooltip.style.top = top + 'px';
      tooltip.style.left = left + 'px';
    }, 0);
  }

  ngOnDestroy() {
    if (this.hideTimeout) {
      clearTimeout(this.hideTimeout);
    }
    if (this.tooltipElement) {
      this.tooltipElement.remove();
    }
  }
}
