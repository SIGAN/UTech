import { Event, EventDTO } from '../models/event.model';
import { Comment } from '../models/comment.model';

// Test date constants
export const TEST_DATE_UTC = '2024-02-05T10:00:00';
export const TEST_DATE_UTC_END = '2024-02-05T12:00:00';
export const TEST_DATE_LOCAL = new Date(TEST_DATE_UTC + 'Z');
export const TEST_DATE_LOCAL_END = new Date(TEST_DATE_UTC_END + 'Z');

export const mockEvent: Event = {
  id: 1,
  title: 'Test Event',
  description: 'Test Description',
  place: 'Test Place',
  start_time: TEST_DATE_LOCAL,
  end_time: TEST_DATE_LOCAL_END,
  food: 'Test Food',
  drinks: 'Test Drinks',
  program: 'Test Program',
  parking_info: 'Test Parking',
  music: 'Test Music',
  theme: 'Test Theme',
  age_restrictions: '18+',
  author_email: 'test@example.com'
};

export const mockEventDTO: EventDTO = {
  id: 1,
  title: 'Test Event',
  description: 'Test Description',
  place: 'Test Place',
  start_time: TEST_DATE_UTC,
  end_time: TEST_DATE_UTC_END,
  food: 'Test Food',
  drinks: 'Test Drinks',
  program: 'Test Program',
  parking_info: 'Test Parking',
  music: 'Test Music',
  theme: 'Test Theme',
  age_restrictions: '18+',
  author_email: 'test@example.com'
};

export const mockErrorResponse = {
  unauthorized: {
    status: 401,
    statusText: 'Unauthorized',
    error: { detail: 'Invalid or expired session' }
  },
  forbidden: {
    status: 403,
    statusText: 'Forbidden',
    error: { detail: 'not authorized to perform this action' }
  },
  notFound: {
    status: 404,
    statusText: 'Not Found',
    error: { detail: 'Resource not found' }
  },
  serverError: {
    status: 500,
    statusText: 'Internal Server Error',
    error: { detail: 'Server error' }
  }
};

export const mockComment: Comment = {
  id: 1,
  event_id: 1,
  user_id: 'test@example.com',
  message: 'Test Comment',
  rating: 5,
  author_email: 'test@example.com'
};