// Interface for API requests/responses (UTC times as strings)
export interface EventDTO {
    id?: number;
    title: string;
    description?: string;
    place?: string;
    start_time?: string; // UTC time in ISO format without timezone
    end_time?: string;   // UTC time in ISO format without timezone
    food?: string;
    drinks?: string;
    program?: string;
    parking_info?: string;
    music?: string;
    theme?: string;
    age_restrictions?: string;
    author_email: string;
}

// Interface for frontend use (local times as Date objects)
export interface Event {
    id?: number;
    title: string;
    description?: string;
    place?: string;
    start_time?: Date;  // Local time as Date object
    end_time?: Date;    // Local time as Date object
    food?: string;
    drinks?: string;
    program?: string;
    parking_info?: string;
    music?: string;
    theme?: string;
    age_restrictions?: string;
    author_email: string;
}

// Helper functions to convert between DTO and frontend model
export function toEventDTO(event: Event): EventDTO {
    const { start_time, end_time, ...rest } = event;
    return {
        ...rest,
        start_time: start_time?.toISOString().slice(0, 19), // Remove timezone part
        end_time: end_time?.toISOString().slice(0, 19)      // Remove timezone part
    };
}

export function fromEventDTO(dto: EventDTO): Event {
    const { start_time, end_time, ...rest } = dto;
    return {
        ...rest,
        start_time: start_time ? new Date(start_time + 'Z') : undefined, // Add Z to parse as UTC
        end_time: end_time ? new Date(end_time + 'Z') : undefined       // Add Z to parse as UTC
    };
}