import React, { useRef, useEffect, useState } from 'react';
import { Box } from '@mui/material';

export default function MyComponent() {
  const parentRef = useRef(null);
  const [parentWidth, setParentWidth] = useState(0);

  useEffect(() => {
    // Get the width of the parent element
    if (parentRef.current) {
      setParentWidth(parentRef.current.offsetWidth);
    }

    // Optionally add a resize listener to update width on resize
    const handleResize = () => {
      if (parentRef.current) {
        setParentWidth(parentRef.current.offsetWidth);
      }
    };

    window.addEventListener('resize', handleResize);

    // Clean up the resize listener
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <Box ref={parentRef} sx={{ width: '100%' }}>
      <p>Parent width: {parentWidth}px</p>
      {/* Your other components */}
    </Box>
  );
}
