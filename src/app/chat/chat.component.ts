import { Component } from '@angular/core';
import { InputComponent } from './input/input.component';
import { MessagesComponent } from './messages/messages.component';

@Component({
  selector: 'app-chat',
  imports: [InputComponent, MessagesComponent],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.css',
})
export class ChatComponent {}
