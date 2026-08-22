/**
 * Language state, and the single `t()` every component uses.
 *
 * A plain context rather than an i18n library: there are two languages, no
 * pluralisation rules, no date formatting and no interpolation, so a library would
 * add a dependency and a build step without removing any code.
 *
 * The choice is persisted in `localStorage` (not `sessionStorage`) because a language
 * preference is genuinely per-browser and sharing it across tabs is correct -- unlike
 * the party token, where sharing across tabs would break the two-role demo. See
 * `state/session.ts`.
 *
 * `document.documentElement.lang` is kept in step, so a screen reader switches voice
 * with the button instead of reading Devanagari with an English voice.
 */

import {
  createContext,
  createElement,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type { Bilingual, Lang } from "../api/types";
import { loadLang, saveLang } from "../state/session";
import { phrase, type UiKey } from "./strings";

export interface LangContextValue {
  lang: Lang;
  setLang: (next: Lang) => void;
  /** Interface chrome. Compile error on an unknown key. */
  t: (key: UiKey) => string;
  /** Server-supplied bilingual copy, rendered verbatim. */
  s: (value: Bilingual | null | undefined) => string;
}

const LangContext = createContext<LangContextValue | null>(null);

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => loadLang("en"));

  useEffect(() => {
    const root = globalThis.document?.documentElement;
    if (root) root.lang = lang;
  }, [lang]);

  const setLang = useCallback((next: Lang) => {
    setLangState(next);
    saveLang(next);
  }, []);

  const value = useMemo<LangContextValue>(
    () => ({
      lang,
      setLang,
      t: (key: UiKey) => phrase(key, lang),
      s: (bilingual: Bilingual | null | undefined) => bilingual?.[lang] ?? "",
    }),
    [lang, setLang],
  );

  return createElement(LangContext.Provider, { value }, children);
}

export function useLang(): LangContextValue {
  const value = useContext(LangContext);
  if (!value) throw new Error("useLang must be used inside <LangProvider>");
  return value;
}
