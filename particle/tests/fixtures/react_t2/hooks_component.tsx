// Test fixture: React functional component with hooks
import React, { useState, useEffect, useCallback, useMemo, useContext, useRef } from 'react';

const ThemeContext = React.createContext('light');

// Custom hook using useState - should be EXT.REACT.005
function useCounter(initial: number = 0) {
  const [count, setCount] = useState(initial);
  const increment = useCallback(() => setCount(c => c + 1), []);
  return { count, increment };
}

// Functional component with hooks - should be EXT.REACT.001 or EXT.REACT.006
function Counter({ label }: { label: string }) {
  const { count, increment } = useCounter(0);
  const theme = useContext(ThemeContext);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    document.title = `Count: ${count}`;
  }, [count]);

  const doubled = useMemo(() => count * 2, [count]);

  return (
    <div ref={ref} className={theme}>
      <h2>{label}</h2>
      <p>Count: {count} (doubled: {doubled})</p>
      <button onClick={increment}>+</button>
    </div>
  );
}

// Root component - should be EXT.REACT.001
function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Counter label="My Counter" />
    </ThemeContext.Provider>
  );
}

export default App;
