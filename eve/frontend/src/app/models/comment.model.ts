export interface Comment {
    id?: number;
    event_id: number;
    user_id: string;
    message: string;
    rating: number;
    author_email?: string;
}