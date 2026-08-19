import { Star } from "lucide-react";

export function RatingControl({ value, onChange }: { value: number | null; onChange: (rating: number) => void }) {
  return (
    <div className="rating-control" aria-label="Your rating">
      {[1, 2, 3, 4, 5].map((rating) => (
        <button
          key={rating}
          type="button"
          className={rating <= (value ?? 0) ? "rated" : ""}
          aria-label={`Rate ${rating} out of 5`}
          onClick={() => onChange(rating)}
        >
          <Star size={20} fill="currentColor" />
        </button>
      ))}
    </div>
  );
}