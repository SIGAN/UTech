import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { EventService } from '../../services/event.service';
import { AuthService } from '../../services/auth.service';
import { DateService } from '../../services/date.service';
import { ErrorService } from '../../services/error.service';
import { Event } from '../../models/event.model';

@Component({
  selector: 'app-event-form',
  templateUrl: './event-form.component.html',
  styleUrls: ['./event-form.component.scss']
})
export class EventFormComponent implements OnInit {
  eventForm: FormGroup;
  isEditMode = false;
  eventId: number | null = null;

  constructor(
    private fb: FormBuilder,
    private eventService: EventService,
    private authService: AuthService,
    private dateService: DateService,
    private errorService: ErrorService,
    private router: Router,
    private route: ActivatedRoute
  ) {
    this.eventForm = this.fb.group({
      title: ['', Validators.required],
      description: [''],
      place: [''],
      start_date: [''],
      start_time: [''],
      end_date: [''],
      end_time: [''],
      food: [''],
      drinks: [''],
      program: [''],
      parking_info: [''],
      music: [''],
      theme: [''],
      age_restrictions: ['']
    });
  }

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEditMode = true;
      this.eventId = parseInt(id, 10);
      this.loadEvent(this.eventId);
    }
  }

  loadEvent(id: number) {
    this.eventService.getEvent(id).subscribe({
      next: (event) => {
        // Convert UTC dates to local time
        const localStartTime = event.start_time ? this.dateService.fromUTC(event.start_time.toISOString().slice(0, 19)) : undefined;
        const localEndTime = event.end_time ? this.dateService.fromUTC(event.end_time.toISOString().slice(0, 19)) : undefined;

        this.eventForm.patchValue({
          ...event,
          start_date: localStartTime || '',
          start_time: localStartTime ? localStartTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }) : '',
          end_date: localEndTime || '',
          end_time: localEndTime ? localEndTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }) : ''
        });
      },
      error: () => this.router.navigate(['/events'])
    });
  }

  onSubmit() {
    if (this.eventForm.valid) {
      const formValue = this.eventForm.value;
      const currentUserEmail = this.authService.getCurrentUserEmail();
      if (!currentUserEmail) return;

      // Create local Date objects from form values if dates are provided
      let startDate: Date | undefined;
      let endDate: Date | undefined;

      if (formValue.start_date && formValue.start_time) {
        startDate = new Date(formValue.start_date);
        const [startHours, startMinutes] = formValue.start_time.split(':');
        startDate.setHours(parseInt(startHours, 10), parseInt(startMinutes, 10));
        // do not convert to UTC, cause you actually don't, dates in JS are always zone-aware!
      }

      if (formValue.end_date && formValue.end_time) {
        endDate = new Date(formValue.end_date);
        const [endHours, endMinutes] = formValue.end_time.split(':');
        endDate.setHours(parseInt(endHours, 10), parseInt(endMinutes, 10));
        // do not convert to UTC, cause you actually don't, dates in JS are always zone-aware!
      }

      const eventData: Event = {
        title: formValue.title,
        description: formValue.description,
        place: formValue.place,
        start_time: startDate,
        end_time: endDate,
        food: formValue.food || undefined,
        drinks: formValue.drinks || undefined,
        program: formValue.program || undefined,
        parking_info: formValue.parking_info || undefined,
        music: formValue.music || undefined,
        theme: formValue.theme || undefined,
        age_restrictions: formValue.age_restrictions || undefined,
        author_email: currentUserEmail
      };

      if (this.isEditMode && this.eventId) {
        this.eventService.updateEvent(this.eventId, eventData).subscribe({
          next: () => {
            this.router.navigate(['/events']).catch(err => {
              console.error('Navigation failed:', err);
              window.location.href = '/events';
            });
          },
          error: (error) => {
            console.error('Failed to update event:', error);
            this.errorService.showError('Failed to update event. Please try again.');
            this.router.navigate(['/events']);
          }
        });
      } else {
        this.eventService.createEvent(eventData).subscribe({
          next: () => {
            this.router.navigate(['/events']).catch(err => {
              console.error('Navigation failed:', err);
              window.location.href = '/events';
            });
          },
          error: (error) => {
            console.error('Failed to create event:', error);
            this.errorService.showError('Failed to create event. Please try again.');
          }
        });
      }
    }
  }

  onCancel() {
    this.router.navigate(['/events']);
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