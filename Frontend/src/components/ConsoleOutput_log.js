import React, { useEffect, useRef, useState } from 'react';
import { io } from 'socket.io-client';
import { Box, Typography } from '@mui/material';
import { useJobContext } from './context/JobContext';

// Uncomment this if socket connection is needed
// const socket = io(process.env.REACT_APP_BACKEND); // Adjust the URL if needed

const ConsoleOutput_log = ({ content }) => { // Accept content as a prop
  const { viewStatus, setViewStatus } = useJobContext();
  const [output, setOutput] = useState(content || ''); // Initialize output with content
  const preRef = useRef(null); // Create a ref for the <pre> element

  useEffect(() => {
    // Function to update output when content changes
    setOutput(content); // Update output whenever content prop changes
  }, [content]); // Effect runs whenever content changes

  // If you're using socket to listen for updates, you can add the socket logic here
  useEffect(() => {
    // Listen for socket events if necessary
    // socket.on('your_socket_event', (data) => {
    //   setOutput((prevOutput) => prevOutput + '\n' + data); // Update output with new data
    // });

    // Clean up on component unmount
    return () => {
      // socket.off('your_socket_event'); // Uncomment if using socket
    };
  }, []); // Empty array means this runs once on mount

  return (
    <Box
      sx={{
        bgcolor: '#1e1e1e',  // Dark background for console style
        color: 'white',       // Change text color to white
        padding: '16px',
        borderRadius: '8px',
        height: '500px',
        overflowY: 'auto',    // Enable scrolling when logs exceed height
        fontFamily: 'monospace', // Monospace font for a console-like feel
        width: '100%',
      }}
    >
      <Typography variant="h6" gutterBottom>
        Console Output
      </Typography>

      <pre
        ref={preRef} // Attach ref for scrolling if needed
        style={{
          backgroundColor: 'black',
          color: 'white',
          padding: '10px',
          height: '400px',
          overflowY: 'scroll',
          textAlign: 'left',
          width: '100%',
        }}
      >
        {output} {/* Display the output here */}
        <br />
        <br />
      </pre>
    </Box>
  );
};

export default ConsoleOutput_log;
