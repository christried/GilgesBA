import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'removeSources',
})
export class RemoveSourcesPipe implements PipeTransform {
  transform(value: string): string {
    if (!value) return value;
    // Remove all occurrences of 【...】
    return value.replace(/【.*?】/g, '');
  }
}
