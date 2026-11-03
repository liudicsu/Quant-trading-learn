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
  hours: number;
  difficulty: number;
  skippable: boolean;
  skipNote?: L10n;
  hourBasis: string;
  prereqs: string[];
  goals: L10n[];
  mustTeach: L10n[];
  exercises: L10n[];
  quizTopics: L10n[];
  doneWhen: L10n[];
  methodTags: { classic: string[]; niche: string[]; frontier: string[] };
  tasks: Task[];
  status: LessonStatus;
}

export interface Phase {
  id: string;
  slug: string;
  title: L10n;
  goal: L10n;
  cluster: string;
  lessons: Lesson[];
}
