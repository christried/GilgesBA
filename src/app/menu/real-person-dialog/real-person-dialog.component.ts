import { ChangeDetectionStrategy, Component, model } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-real-person-dialog',
  imports: [
    MatDialogModule,
    MatButtonModule,
    MatInputModule,
    MatFormFieldModule,
    FormsModule,
  ],
  templateUrl: './real-person-dialog.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RealPersonDialogComponent {
  readonly email = model('');
}
