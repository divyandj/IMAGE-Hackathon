
// import { createContext, useContext, useEffect, useState } from "react";

// type Theme = "dark" | "light" | "system";

// type ThemeProviderProps = {
//   children: React.ReactNode;
//   defaultTheme?: "light";
//   storageKey?: string;
// };

// type ThemeProviderState = {
//   theme: Theme;
//   setTheme: (theme: Theme) => void;
// };

// const initialState: ThemeProviderState = {
//   theme: "light",
//   setTheme: () => null,
// };

// const ThemeProviderContext = createContext<ThemeProviderState>(initialState);

// export function ThemeProvider({
//   children,
//   defaultTheme = "system",
//   storageKey = "ui-theme",
//   ...props
// }: ThemeProviderProps) {
//   const [theme, setTheme] = useState<Theme>(
//     () => (localStorage.getItem(storageKey) as Theme) || defaultTheme
//   );

//   useEffect(() => {
//     const root = window.document.documentElement;
//     root.classList.remove("light", "dark");

//     if (theme === "system") {
//       const systemTheme = window.matchMedia("(prefers-color-scheme: light)")
//         .matches
//         ? "dark"
//         : "light";
//       root.classList.add(systemTheme);
//       return;
//     }

//     root.classList.add(theme);
//   }, [theme]);

//   const value = {
//     theme,
//     setTheme: (theme: Theme) => {
//       localStorage.setItem(storageKey, theme);
//       setTheme(theme);
//     },
//   };

//   return (
//     <ThemeProviderContext.Provider {...props} value={value}>
//       {children}
//     </ThemeProviderContext.Provider>
//   );
// }

// export const useTheme = () => {
//   const context = useContext(ThemeProviderContext);

//   if (context === undefined)
//     throw new Error("useTheme must be used within a ThemeProvider");

//   return context;
// };


import { createContext, useContext, useEffect, useState } from "react";

type Theme = "light"; // Only light theme is supported now

type ThemeProviderProps = {
  children: React.ReactNode;
  defaultTheme?: "light";
  storageKey?: string;
};

type ThemeProviderState = {
  theme: Theme;
  setTheme: (theme: Theme) => void;
};

const initialState: ThemeProviderState = {
  theme: "light",
  setTheme: () => null,
};

const ThemeProviderContext = createContext<ThemeProviderState>(initialState);

export function ThemeProvider({
  children,
  defaultTheme = "light", // Default is always light
  storageKey = "ui-theme",
  ...props
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(
    () => (localStorage.getItem(storageKey) as Theme) || defaultTheme
  );

  useEffect(() => {
    const root = window.document.documentElement;
    // Only need to manage light theme
    root.classList.remove("dark"); // Just in case it was there before
    root.classList.add("light");
  }, [theme]);

  const value = {
    theme,
    setTheme: (theme: Theme) => {
      localStorage.setItem(storageKey, theme);
      setTheme(theme);
    },
  };

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext);

  if (context === undefined)
    throw new Error("useTheme must be used within a ThemeProvider");

  return context;
};