import { Event, EventDTO, toEventDTO, fromEventDTO } from './event.model';

describe('Event Model', () => {
  const mockLocalDate = new Date('2024-01-01T12:00:00');
  const mockUTCString = '2024-01-01T12:00:00';

  const mockEvent: Event = {
    id: 1,
    title: 'Test Event',
    description: 'Test Description',
    place: 'Test Place',
    start_time: new Date(mockLocalDate),
    end_time: new Date(mockLocalDate),
    author_email: 'test@example.com',
    food: 'Test Food',
    drinks: 'Test Drinks'
  };

  const mockEventDTO: EventDTO = {
    id: 1,
    title: 'Test Event',
    description: 'Test Description',
    place: 'Test Place',
    start_time: mockUTCString,
    end_time: mockUTCString,
    author_email: 'test@example.com',
    food: 'Test Food',
    drinks: 'Test Drinks'
  };

  describe('toEventDTO', () => {
    it('should convert Event to EventDTO', () => {
      const dto = toEventDTO(mockEvent);
      expect(dto.id).toBe(mockEvent.id);
      expect(dto.title).toBe(mockEvent.title);
      expect(dto.description).toBe(mockEvent.description);
      expect(dto.place).toBe(mockEvent.place);
      expect(dto.start_time).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/);
      expect(dto.end_time).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/);
      expect(dto.author_email).toBe(mockEvent.author_email);
    });

    it('should handle optional fields', () => {
      const minimalEvent: Event = {
        title: 'Minimal Event',
        description: 'Description',
        place: 'Place',
        start_time: new Date(mockLocalDate),
        end_time: new Date(mockLocalDate)
      };

      const dto = toEventDTO(minimalEvent);
      expect(dto.food).toBeUndefined();
      expect(dto.drinks).toBeUndefined();
      expect(dto.program).toBeUndefined();
      expect(dto.parking_info).toBeUndefined();
      expect(dto.music).toBeUndefined();
      expect(dto.theme).toBeUndefined();
      expect(dto.age_restrictions).toBeUndefined();
    });

    it('should convert dates to UTC strings without timezone info', () => {
      const dto = toEventDTO(mockEvent);
      expect(dto.start_time).not.toContain('Z');
      expect(dto.start_time).not.toContain('+');
      expect(dto.end_time).not.toContain('Z');
      expect(dto.end_time).not.toContain('+');
    });
  });

  describe('fromEventDTO', () => {
    it('should convert EventDTO to Event', () => {
      const event = fromEventDTO(mockEventDTO);
      expect(event.id).toBe(mockEventDTO.id);
      expect(event.title).toBe(mockEventDTO.title);
      expect(event.description).toBe(mockEventDTO.description);
      expect(event.place).toBe(mockEventDTO.place);
      expect(event.start_time).toBeInstanceOf(Date);
      expect(event.end_time).toBeInstanceOf(Date);
      expect(event.author_email).toBe(mockEventDTO.author_email);
    });

    it('should handle optional fields', () => {
      const minimalDTO: EventDTO = {
        title: 'Minimal Event',
        description: 'Description',
        place: 'Place',
        start_time: mockUTCString,
        end_time: mockUTCString
      };

      const event = fromEventDTO(minimalDTO);
      expect(event.food).toBeUndefined();
      expect(event.drinks).toBeUndefined();
      expect(event.program).toBeUndefined();
      expect(event.parking_info).toBeUndefined();
      expect(event.music).toBeUndefined();
      expect(event.theme).toBeUndefined();
      expect(event.age_restrictions).toBeUndefined();
    });

    it('should convert UTC strings to local Date objects', () => {
      const event = fromEventDTO(mockEventDTO);
      expect(event.start_time?.getTime()).toBe(new Date(mockEventDTO.start_time + 'Z').getTime());
      expect(event.end_time?.getTime()).toBe(new Date(mockEventDTO.end_time + 'Z').getTime());
    });
  });
});