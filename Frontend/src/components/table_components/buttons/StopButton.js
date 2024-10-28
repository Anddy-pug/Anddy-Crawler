// components/StopButton.js
import React from 'react';
import Button from '@mui/material/Button';
import StopIcon from '@mui/icons-material/Stop'; // Import StopIcon

const StopButton = ({ onClick }) => {
  return (
    <Button
      variant="contained"
      size="small"
      startIcon={<StopIcon />} // Use StopIcon here
      onClick={onClick}
      sx={{
        backgroundColor: 'red',
        color: 'white',
        minWidth: '10px',
        '&:hover': {
          backgroundColor: 'darkred',
        },
      }}
    >
      
    </Button>
  );
};

export default StopButton;
