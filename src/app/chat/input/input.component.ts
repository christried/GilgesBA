import { Component, inject, ViewChild } from '@angular/core';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import {
  FormsModule,
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MessagesService } from '../messages/messages.service';
import { TextFieldModule } from '@angular/cdk/text-field';
import { MatDialogModule } from '@angular/material/dialog';

@Component({
  selector: 'app-input',
  standalone: true,
  imports: [
    MatInputModule,
    MatFormFieldModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    ReactiveFormsModule,
    TextFieldModule,
    MatDialogModule,
  ],
  templateUrl: './input.component.html',
  styleUrls: ['./input.component.css'],
})
export class InputComponent {
  private messagesService = inject(MessagesService);

  form = new FormGroup({
    message: new FormControl('', {
      validators: [Validators.required],
      nonNullable: true,
    }),
  });

  handleKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      if (this.form.valid && this.form.value.message?.trim()) {
        this.onSubmit();
      }
    }
  }

  onSubmit() {
    if (this.form.invalid || !this.form.value.message?.trim()) {
      return;
    }

    const messageContent = this.form.value.message as string;
    this.messagesService.addMessage(messageContent);

    this.form.reset();
  }
}
