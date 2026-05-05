import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="text-center max-w-md mx-auto mt-16 space-y-4">
      <p className="font-mono text-xs uppercase tracking-widest text-ink-500">404</p>
      <h2 className="text-2xl font-semibold text-ink-100">Page not found</h2>
      <p className="text-sm text-ink-400">
        That route doesn&apos;t exist. Maybe you meant the lab or the eval page.
      </p>
      <div className="flex justify-center gap-2">
        <Button variant="primary">
          <Link href="/">Lab</Link>
        </Button>
        <Button variant="secondary">
          <Link href="/eval">Eval</Link>
        </Button>
      </div>
    </div>
  );
}
