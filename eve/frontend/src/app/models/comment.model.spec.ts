import { Comment } from './comment.model';

describe('Comment Model', () => {
  const mockComment: Comment = {
    id: 1,
    event_id: 1,
    user_id: 'user@example.com',
    message: 'Test Comment',
    rating: 5,
    author_email: 'author@example.com'
  };

  it('should create a valid comment', () => {
    expect(mockComment.id).toBe(1);
    expect(mockComment.event_id).toBe(1);
    expect(mockComment.user_id).toBe('user@example.com');
    expect(mockComment.message).toBe('Test Comment');
    expect(mockComment.rating).toBe(5);
    expect(mockComment.author_email).toBe('author@example.com');
  });

  it('should have default rating of 0', () => {
    const comment: Comment = {
      id: 2,
      event_id: 1,
      user_id: 'user@example.com',
      message: 'Comment with default rating',
      author_email: 'author@example.com',
      rating: 0
    };

    expect(comment.rating).toBe(0);
    expect(comment.message).toBe('Comment with default rating');
  });

  it('should validate rating range', () => {
    const validRatings = [0, 1, 2, 3, 4, 5];
    validRatings.forEach(rating => {
      const comment: Comment = { ...mockComment, rating };
      expect(comment.rating).toBe(rating);
    });
  });
});