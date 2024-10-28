import React, { useEffect, useRef, useState } from 'react';
import { io } from 'socket.io-client';
import { Box, Typography } from '@mui/material';
import { useJobContext } from './context/JobContext';

// const socket = io(process.env.REACT_APP_BACKEND); // Adjust the URL if needed

const ConsoleOutput = () => {
  const socket = io(process.env.REACT_APP_BACKEND, { // Replace with your server URL
    query: {
      username: 'file' // Replace with the actual username
    }
  });

  let socket_field_name = '';

  const { viewStatus, setViewStatus } = useJobContext();
  const [output, setOutput] = useState('');
  const preRef = useRef(null); // Create a ref for the <pre> element
  const [loading, setLoading] = useState(true); // Loading state

  // Determine socket field name based on view status
  socket_field_name = viewStatus;

  useEffect(() => {
    // Function to fetch initial data from the API
    const fetchInitialData = async () => {
      try {
        // Construct the query parameters
        const jsonData = { 'job_name': socket_field_name }; // Example data
        const queryString = new URLSearchParams(jsonData).toString(); // Convert to query string
        
        // Make the GET request with query parameters
        const response = await fetch(`${process.env.REACT_APP_BACKEND}/get_console?${queryString}`, {
          method: 'GET', // Use GET for query parameters
          headers: {
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        let joinedString = data[socket_field_name].join('\n');
        setOutput(joinedString); // Assuming your API response has an 'output' property
      } catch (error) {
        console.error('Error fetching initial data:', error);
        setOutput('Error fetching initial data.'); // Display error message in output
      } finally {
        setLoading(false); // Set loading to false regardless of success or error
      }
    };

    // Fetch initial data when the component mounts
    fetchInitialData();

    // Listen for socket events
    socket.on(socket_field_name, (data) => {
      setOutput((prevOutput) => {
        const newOutput = prevOutput + data + '\n';
        // Scroll to the bottom whenever new output is added
        if (preRef.current) {
          preRef.current.scrollTop = preRef.current.scrollHeight;
        }
        return newOutput;
      });
    });

    // Clean up on component unmount
    return () => {
      socket.off(socket_field_name);
    };
  }, [socket_field_name]); // Include socket_field_name in the dependency array

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
      }}
    >
      <Typography variant="h6" gutterBottom>
        Console Output
      </Typography>

      <pre
        ref={preRef} // Attach the ref to the <pre> element
        style={{
          backgroundColor: 'black',
          color: 'white',
          padding: '10px',
          height: '400px',
          overflowY: 'scroll',
          textAlign: 'left',
        }}
      >
        {output}
        <br />
        <br />
      </pre>
    </Box>
  );
};

export default ConsoleOutput;
