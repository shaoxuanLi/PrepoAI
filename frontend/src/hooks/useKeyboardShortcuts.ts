import { useEffect } from "react";

type ShortcutHandler = (event: KeyboardEvent) => void;

export function useKeyboardShortcuts(bindings: Record<string, ShortcutHandler>, active = true): void {
  useEffect(() => {
    if (!active) {
      return;
    }

    const onKeyDown = (event: KeyboardEvent) => {
      const handler = bindings[event.key.toLowerCase()];
      if (!handler) {
        return;
      }

      event.preventDefault();
      handler(event);
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [bindings, active]);
}
