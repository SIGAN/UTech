import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class DateService {
  toUTC(localDate: Date): string {
    const utcDate = new Date(localDate.getTime() - localDate.getTimezoneOffset() * 60000);
    return utcDate.toISOString().slice(0, 19);
  }

  fromUTC(utcString: string): Date {
    return new Date(utcString + 'Z');
  }

  formatForDisplay(utcDate?: string | Date): string {
    if (!utcDate) return 'Not set';
    const date = typeof utcDate === 'string' ? this.fromUTC(utcDate) : utcDate;
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}