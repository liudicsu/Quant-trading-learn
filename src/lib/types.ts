export type Locale = "zh" | "en";
export type L10n = Record<Locale, string>;
export type LessonStatus = "ready" | "outline";

export interface Task {
  id: string;
  text: L10n;
}

export interface Lesson {
  slug: string;
  title: L10n;
  summary: L10n;
  minutes: number;
  resources: string[];
  tasks: Task[];
  objectives?: L10n[];
  prereqs?: string[];
  mustTeach?: L10n[];
  pitfalls?: L10n[];
  status: LessonStatus;
}

export interface Month {
  id: number;
  slug: string;
  title: L10n;
  goal: L10n;
  topics: L10n[];
  milestones: L10n[];
  lessons: Lesson[];
}
