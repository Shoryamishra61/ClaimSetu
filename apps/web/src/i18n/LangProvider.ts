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
import { phrase, type Lang } from "./strings";

const LANG_KEY = "identity-rescue.lang.v1";
function initialLang(): Lang {
  try {
    return localStorage.getItem(LANG_KEY) === "hi" ? "hi" : "en";
  } catch {
    return "en";
  }
}

interface LangContextValue {
  lang: Lang;
  setLang: (next: Lang) => void;
  t: (key: string) => string;
}
const LangContext = createContext<LangContextValue | null>(null);

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(initialLang);
  useEffect(() => {
    document.documentElement.lang = lang === "hi" ? "hi-IN" : "en-IN";
  }, [lang]);
  const setLang = useCallback((next: Lang) => {
    setLangState(next);
    try {
      localStorage.setItem(LANG_KEY, next);
    } catch {
      /* current page still works */
    }
  }, []);
  const value = useMemo(
    () => ({ lang, setLang, t: (key: string) => phrase(key, lang) }),
    [lang, setLang],
  );
  return createElement(LangContext.Provider, { value }, children);
}

export function useLang(): LangContextValue {
  const value = useContext(LangContext);
  if (!value) throw new Error("useLang must be used inside LangProvider");
  return value;
}
