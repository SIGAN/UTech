import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { AuthService } from '../services/auth.service';
import { EventService } from '../services/event.service';
import { DateService } from '../services/date.service';
import { Event } from '../models/event.model';
import { ConfirmDialogComponent } from '../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-events',
  standalone: false,
  templateUrl: './events.component.html',
  styleUrls: ['./events.component.css']
})
export class EventsComponent implements OnInit {
  events: Event[] = [];
  currentUserEmail: string = '';

  constructor(
    private authService: AuthService,
    private eventService: EventService,
    public dateService: DateService,
    private router: Router,
    private dialog: MatDialog
  ) {
    this.currentUserEmail = this.authService.getCurrentUserEmail() || '';
  }

  ngOnInit() {
    this.loadEvents();
  }

  loadEvents() {
    this.eventService.getEvents().subscribe({
      next: (events) => {
        this.events = events;
      },
      error: (error) => {
        console.error('Failed to load events:', error);
      }
    });
  }

  createEvent() {
    this.router.navigate(['/events/new']);
  }

  editEvent(event: Event) {
    if (event.id === undefined) {
      console.error('Event ID is undefined');
      return;
    }
    this.router.navigate(['/events', event.id, 'edit']);
  }

  deleteEvent(event: Event) {
    if (event.id === undefined) {
      console.error('Event ID is undefined');
      return;
    }
    
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: { message: 'Are you sure you want to delete this event?' }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.eventService.deleteEvent(event.id!).subscribe({
          next: () => {
            // Remove the event from the local array immediately
            this.events = this.events.filter(e => e.id !== event.id);
          },
          error: (error) => {
            console.error('Failed to delete event:', error);
          }
        });
      }
    });
  }

  onLogout() {
    this.authService.logout().subscribe({
      next: () => {
        this.router.navigate(['/login']);
      },
      error: (error) => {
        console.error('Logout failed:', error);
        // Even if the API call fails, we should still clear local storage and redirect
        this.router.navigate(['/login']);
      }
    });
  }
}
