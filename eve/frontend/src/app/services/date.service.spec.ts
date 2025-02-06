import { TestBed } from '@angular/core/testing';
import { DateService } from './date.service';

describe('DateService', () => {
  let service: DateService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DateService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('toUTC', () => {
    it('should convert local date string to UTC string without timezone info', () => {
      // Create a specific local date
      const localDate = new Date(2024, 0, 1, 12, 0, 0); // Jan 1, 2024, 12:00:00 local time
      const result = service.toUTC(localDate);
      
      // Get expected UTC hours based on local timezone offset
      const offset = localDate.getTimezoneOffset();
      const expectedHour = (12 + offset / 60) % 24;
      
      // Expected format: YYYY-MM-DDThh:mm:ss
      expect(result).toMatch(/^2024-01-01T\d{2}:00:00$/);
      expect(result.split('T')[1].split(':')[0]).toBe(expectedHour.toString().padStart(2, '0'));
    });
  });

  describe('fromUTC', () => {
    it('should convert UTC string to local Date object', () => {
      const utcString = '2024-01-01T12:00:00';
      const result = service.fromUTC(utcString);
      
      expect(result).toBeInstanceOf(Date);
      // The resulting date should be offset by the local timezone
      const expectedLocal = new Date(utcString + 'Z');
      expect(result.getTime()).toBe(expectedLocal.getTime());
    });
  });

  describe('formatForDisplay', () => {
    it('should format date for display', () => {
      const date = new Date(2024, 0, 1, 12, 0, 0);
      const result = service.formatForDisplay(date);
      
      // The exact format will depend on the locale, but should include year, month, day, hour, and minute
      expect(result).toContain('2024');
      expect(result).toContain('12');
      expect(result).toContain('00');
    });
  });
});