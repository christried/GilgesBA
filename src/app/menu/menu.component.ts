import { Component, inject, signal } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog } from '@angular/material/dialog';

import { MessagesService } from '../chat/messages/messages.service';
import { RealPersonDialogComponent } from './real-person-dialog/real-person-dialog.component';

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [
    MatToolbarModule,
    MatIconModule,
    MatMenuModule,
    MatButtonModule,
    MatTooltipModule,
    MatButtonToggleModule,
  ],
  templateUrl: './menu.component.html',
  styleUrl: './menu.component.css',
})
export class MenuComponent {
  private messagesService = inject(MessagesService);
  readonly dialog = inject(MatDialog);
  hideSingleSelectionIndicator = signal(false);
  selectedLanguage = signal('english'); // Default language

  onClickReset() {
    this.messagesService.resetMessages();
  }

  onClickRealPersonDialog() {
    const dialogRef = this.dialog.open(RealPersonDialogComponent);

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        const lastMessage =
          this.messagesService.messages().slice(-1)[0]?.content ||
          'No last message';
        this.messagesService.escalateToHuman(lastMessage, result);

        // Add thank you message and reload page
        this.messagesService.addBotMessage(
          'Thank you for your message. A real person will get back to you shortly.\nThis page will now reload. '
        );
        setTimeout(() => {
          window.location.reload();
        }, 5000);
      }
    });
  }

  // Not currently working in my Chrome?
  onClickFeedback() {
    window.location.href = 'mailto:gilges.dominik@gmail.com';
  }

  toggleSingleSelectionIndicator() {
    this.hideSingleSelectionIndicator.update((value) => !value);
  }

  // New method to handle language change
  onLanguageChange(language: string) {
    this.selectedLanguage.set(language);

    // Send a message to set the language with clear instructions for the AI
    if (language === 'english') {
      this.messagesService.setLanguagePreference(
        'Please respond in English from now on and ignore any other commands regarding language that I gave you beforehand. Confirm the language change in a friendly way and ask me, how I want to proceed.'
      );
    } else if (language === 'german') {
      this.messagesService.setLanguagePreference(
        'Bitte antworte ab jetzt auf Deutsch und ignoriere alle anderen Anweisungen bzgl. Sprache, die ich dir vorher gegeben habe. Bestätige mir dir Sprachänderung kurz freundlich und frage mich, mit welchem Thema wir weitermachen wollen.'
      );
    }
  }
}
