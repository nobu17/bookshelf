import LoadingSpinner from "../parts/LoadingSpinner";
import { useGlobalSpinnerContext } from "../contexts/GlobalSpinnerContext";

const GlobalSpinner = () => {
  const { isSpinnerOn } = useGlobalSpinnerContext();

  return (
    <>
      {isSpinnerOn && <LoadingSpinner isLoading={true} message="Loading..." />}
    </>
  );
};

export default GlobalSpinner;
