import { useState, useEffect } from 'react';

export const useWindowSize = () => {

  const [size, setSize] = useState({});

  useEffect(() => {
    function onResize() {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });

    }
    window.addEventListener('resize', onResize);
    onResize();
    return () => window.removeEventListener('resize', onResize);

  }, []);
  return size;
}
