export interface Message {
  id: number;
  from: 'bot' | 'user';
  content: string;
  timestamp: Date;
}

export type Messages = Message[];
