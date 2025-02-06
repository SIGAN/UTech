import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { EventService } from '../../services/event.service';
import { CommentService } from '../../services/comment.service';
import { AuthService } from '../../services/auth.service';
import { DateService } from '../../services/date.service';
import { Event } from '../../models/event.model';
import { Comment } from '../../models/comment.model';

@Component({
  selector: 'app-event-details',
  templateUrl: './event-details.component.html',
  styleUrls: ['./event-details.component.scss']
})
export class EventDetailsComponent implements OnInit {
  event?: Event;
  comments: Comment[] = [];
  commentForm: FormGroup;
  currentUserEmail: string;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private eventService: EventService,
    private commentService: CommentService,
    private authService: AuthService,
    public dateService: DateService,
    private fb: FormBuilder
  ) {
    this.currentUserEmail = this.authService.getUserEmail() || '';
    this.commentForm = this.fb.group({
      message: ['', Validators.required],
      rating: [0]
    });
  }

  ngOnInit() {
    const eventId = this.route.snapshot.paramMap.get('id');
    if (!eventId) {
      this.router.navigate(['/events']);
      return;
    }

    const id = parseInt(eventId, 10);
    if (isNaN(id)) {
      this.router.navigate(['/events']);
      return;
    }

    this.loadEvent(id);
    this.loadComments(id);
  }

  loadEvent(eventId: number) {
    this.eventService.getEvent(eventId).subscribe({
      next: (event) => {
        this.event = event;
      },
      error: (error) => {
        console.error('Failed to load event:', error);
        this.router.navigate(['/events']);
      }
    });
  }

  loadComments(eventId: number) {
    this.commentService.getEventComments(eventId).subscribe({
      next: (comments) => {
        this.comments = comments;
      },
      error: (error) => {
        console.error('Failed to load comments:', error);
      }
    });
  }

  addComment() {
    if (!this.event?.id || this.commentForm.invalid) return;

    const comment = {
      ...this.commentForm.value,
      event_id: this.event.id,
      author_email: this.currentUserEmail
    };

    this.commentService.createComment(this.event.id, comment).subscribe({
      next: (newComment) => {
        this.comments.push(newComment);
        this.commentForm.reset({ rating: 0 });
      },
      error: (error) => {
        console.error('Failed to add comment:', error);
      }
    });
  }

  editComment(comment: Comment) {
    if (!this.event?.id || !comment.id) return;

    // Implement edit functionality
  }

  deleteComment(comment: Comment) {
    if (!this.event?.id || !comment.id) return;

    if (confirm('Are you sure you want to delete this comment?')) {
      this.commentService.deleteComment(this.event.id, comment.id).subscribe({
        next: () => {
          this.comments = this.comments.filter(c => c.id !== comment.id);
        },
        error: (error) => {
          console.error('Failed to delete comment:', error);
        }
      });
    }
  }

  canModifyComment(comment: Comment): boolean {
    return comment.author_email === this.currentUserEmail;
  }

  goBack() {
    this.router.navigate(['/events']);
  }
}