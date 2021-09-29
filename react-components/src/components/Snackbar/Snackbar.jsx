import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { toggleSnackbarClose } from "../redux/actions";

const Snackbar = ({ timeout }) => {
  const dispatch = useDispatch();

  // select the UI states from the redux store
  const SHOW = useSelector((state) => state.toggleSnackbar);
  const MESSAGE = useSelector((state) => state.snackbarMessage);

  // convert the timeout prop to pass into the styled component
  let TIME = (timeout - 500) / 1000 + "s";

  let TIMER;
  function handleTimeout() {
    TIMER = setTimeout(() => {
      dispatch(toggleSnackbarClose());
    }, timeout);
  }

  function handleClose() {
    clearTimeout(TIMER);
    dispatch(toggleSnackbarClose());
  }

  useEffect(() => {
    if (SHOW) {
      handleTimeout();
    }
    return () => {
      clearTimeout(TIMER);
    };
  }, [SHOW, TIMER]);

  return (
    SHOW && (
      <Container time={TIME}>
        <p>{MESSAGE}</p>
      </Container>
    )
  );
};


export default Snackbar;
