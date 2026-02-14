import { Component, OnInit } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { trigger, transition, style, animate } from '@angular/animations';
import { ToastService, Toast } from '../../../core/services/toast.service';
import { successSVG, errorSVG, warningSVG, infoSVG } from '../../utils/svg';

@Component({
  selector: 'app-toast',
  templateUrl: './toast.component.html',
  styleUrls: ['./toast.component.css'],
  animations: [
    trigger('fadeInOut', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateX(400px)' }),
        animate('300ms ease-out', style({ opacity: 1, transform: 'translateX(0)' }))
      ]),
      transition(':leave', [
        animate('300ms ease-in', style({ opacity: 0, transform: 'translateX(400px)' }))
      ])
    ])
  ]
})
export class ToastComponent implements OnInit {
  toasts: Toast[] = [];
  iconMap: { [key: string]: SafeHtml } = {};
  currentTime = new Date();

  constructor(private toastService: ToastService, private sanitizer: DomSanitizer) {
    this.initializeIcons();
    setInterval(() => {
      this.currentTime = new Date();
    }, 1000);
  }

  ngOnInit(): void {
    this.toastService.toasts$.subscribe(toasts => {
      this.toasts = toasts;
    });
  }

  removeToast(id: string): void {
    this.toastService.remove(id);
  }

  getToastTitle(type: string): string {
    const titleMap: { [key: string]: string } = {
      success: 'Success',
      error: 'Error',
      warning: 'Warning',
      info: 'Info'
    };
    return titleMap[type] || 'Notification';
  }

  getToastIcon(type: string): SafeHtml {
    return this.iconMap[type] || this.iconMap['info'];
  }

  getTimeAgo(timestamp?: Date): string {
    if (!timestamp) return 'just now';
    
    const now = this.currentTime;
    const diff = now.getTime() - new Date(timestamp).getTime();
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (seconds < 60) {
      return 'just now';
    } else if (minutes < 60) {
      return `${minutes}m ago`;
    } else if (hours < 24) {
      return `${hours}h ago`;
    } else {
      return new Date(timestamp).toLocaleDateString();
    }
  }

  private initializeIcons(): void {
    this.iconMap['success'] = this.sanitizer.bypassSecurityTrustHtml(successSVG);
    this.iconMap['error'] = this.sanitizer.bypassSecurityTrustHtml(errorSVG);
    this.iconMap['warning'] = this.sanitizer.bypassSecurityTrustHtml(warningSVG);
    this.iconMap['info'] = this.sanitizer.bypassSecurityTrustHtml(infoSVG);
  }
}
