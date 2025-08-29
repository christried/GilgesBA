import {
  Component,
  inject,
  effect,
  ViewChild,
  ElementRef,
} from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { NgClass } from '@angular/common';
import { MarkdownModule } from 'ngx-markdown';
import { RemoveSourcesPipe } from './remove-sources.pipe';

import { MessagesService } from './messages.service';
import { Messages } from './messages.model';

@Component({
  selector: 'app-messages',
  standalone: true,
  imports: [
    MatCardModule,
    MatListModule,
    MatIconModule,
    NgClass,
    MarkdownModule,
    RemoveSourcesPipe,
  ],
  templateUrl: './messages.component.html',
  styleUrls: ['./messages.component.css'],
})
export class MessagesComponent {
  messages: Messages = [];
  private messagesService = inject(MessagesService);

  @ViewChild('scrollable') private scrollableContainer!: ElementRef;

  constructor() {
    effect(() => {
      this.messages = this.messagesService.messages();
      this.scrollToBottom();
    });
  }

  ngAfterViewInit() {
    this.scrollToBottom();
  }

  // Method to scroll to the bottom of the message list
  private scrollToBottom(): void {
    setTimeout(() => {
      if (this.scrollableContainer) {
        this.scrollableContainer.nativeElement.scrollTop =
          this.scrollableContainer.nativeElement.scrollHeight;
      }
    }, 0);
  }
}
