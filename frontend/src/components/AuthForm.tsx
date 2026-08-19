import { ArrowRight } from "lucide-react";
import type { FormEvent, ReactNode } from "react";
import { Link } from "react-router-dom";

interface AuthFormProps {
  eyebrow: string;
  title: string;
  submitLabel: string;
  alternateText: string;
  alternateLabel: string;
  alternateTo: string;
  error: string | null;
  submitting: boolean;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  children: ReactNode;
}

export function AuthForm(props: AuthFormProps) {
  return (
    <section className="account-page">
      <div className="account-intro">
        <p className="kicker">{props.eyebrow}</p>
        <h1>{props.title}</h1>
        <p>Keep recommendations, club notes, and reading plans together in one place.</p>
      </div>
      <form className="account-form" onSubmit={props.onSubmit}>
        {props.children}
        {props.error ? <p className="form-error" role="alert">{props.error}</p> : null}
        <button className="form-submit" disabled={props.submitting} type="submit">
          {props.submitting ? "Please wait..." : props.submitLabel}
          <ArrowRight aria-hidden="true" size={18} />
        </button>
        <p className="form-alternate">
          {props.alternateText} <Link to={props.alternateTo}>{props.alternateLabel}</Link>
        </p>
      </form>
    </section>
  );
}