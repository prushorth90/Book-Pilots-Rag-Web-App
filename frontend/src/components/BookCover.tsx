import { BookOpen } from "lucide-react";

export function BookCover({ url, title }: { url: string | null; title: string }) {
  return url ? (
    <img className="book-cover" src={url} alt={`Cover of ${title}`} loading="lazy" />
  ) : (
    <div className="book-cover cover-fallback" role="img" aria-label={`No cover available for ${title}`}>
      <BookOpen aria-hidden="true" size={34} />
      <span>{title}</span>
    </div>
  );
}