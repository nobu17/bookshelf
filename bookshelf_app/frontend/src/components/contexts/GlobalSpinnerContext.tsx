import React, { useState, useContext, createContext } from "react";

type ContextType = {
  isSpinnerOn: boolean;
  setIsSpinnerOn: React.Dispatch<React.SetStateAction<boolean>>;
};

const GlobalSpinnerContext = createContext<ContextType>({
  isSpinnerOn: false,
  setIsSpinnerOn: () => {},
});

// eslint-disable-next-line react-refresh/only-export-components
export const useGlobalSpinnerContext = (): ContextType =>
  useContext<ContextType>(GlobalSpinnerContext);

interface GlobalSpinnerContextProviderProps {
  children?: React.ReactNode;
}

const GlobalSpinnerContextProvider = ({
  children,
}: GlobalSpinnerContextProviderProps) => {
  const [isSpinnerOn, setIsSpinnerOn] = useState(false);

  const values = {
    isSpinnerOn,
    setIsSpinnerOn,
  };

  return (
    <GlobalSpinnerContext.Provider value={values}>
      {children}
    </GlobalSpinnerContext.Provider>
  );
};

export default GlobalSpinnerContextProvider;
