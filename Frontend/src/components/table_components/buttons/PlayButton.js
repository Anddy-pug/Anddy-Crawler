// components/PlayButton.js
import React from 'react';
import Button from '@mui/material/Button';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

const PlayButton = ({ onClick }) => {
  return (
    <Button
      variant="contained"
      size="small"
      startIcon={<PlayArrowIcon />}
      onClick={onClick}
      sx={{
        backgroundColor: 'green',
        color: 'white',
        minWidth: '10px',
        '&:hover': {
          backgroundColor: 'darkgreen',
        },
      }}
    >
        
    </Button>
  );
};

export default PlayButton;
