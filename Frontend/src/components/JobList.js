import Box from '@mui/material/Box';
import { DataGrid } from '@mui/x-data-grid';
import PlayButton from './table_components/buttons/PlayButton';
import StopButton from './table_components/buttons/StopButton';
import Stack from '@mui/material/Stack';
import CircularProgress from '@mui/material/CircularProgress';
import Chip from '@mui/material/Chip';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid2';
import Typography from '@mui/material/Typography';
import PropTypes from 'prop-types';
import AddJobModal from './modal/AddJobModal';
import ContentTitle from './ContentTitle';
import ConsoleDrawer from './ConsoleDrawer';
import { io } from 'socket.io-client';
import axios from 'axios';
import { useJobContext  } from './context/JobContext';
import React, { useEffect, useRef, useState, useCallback, useLayoutEffect } from 'react';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import IconButton from '@mui/material/IconButton';
import FlexGrid from './DisableStopEditModeOnFocusOut'
// pip install fitz aspose moviepy pandas csv openpyxl
// pip install flask_socketio  flask flask_cors tika watchdog  typing selenium  webdriver_manager elasticsearch bs4 colorama scrapy numpy requests langdetect apscheduler

console.log(process.env.REACT_APP_BACKEND);

const socket = io(process.env.REACT_APP_BACKEND);

let job_status = {};

function listenForJobStatus() {
  return new Promise((resolve) => {
      socket.on('job_status', (data) => {
          // job_status = data;
          resolve(data);  // Resolve the promise with the updated status
      });
  });
}

job_status = await listenForJobStatus();


export default function JobList() {



  // useEffect(() => {
  //   socket.on('job_status', (data) => {
  //     job_status = data;
  //   });

  //   return () => {
  //     socket.off("job_status"); // Clean up on component unmount
  //   };
  // }, []);


  const { viewStatus, setViewStatus } = useJobContext();
  const handlePlayButtonClick = (row, rows, setRows) => {

    console.log('Play button clicked for row:', row);
  
    // Emit the start event based on job type
    if (row.job_type === 'File Crawling') {
      socket.emit('start_file_process', { username: row.job_name });
    } else if (row.job_type === 'Web Crawling') {
      socket.emit('start_web_process', { username: row.job_name });
    }
  
    // Update the row to show StopButton
    const updatedRows = rows.map((r) =>
      r.id === row.id ? { ...r, job_button: true } : r
    );
    setRows(updatedRows);
  };
  
  const handleStopButtonClick = (row, rows, setRows) => {
    const socket = io(process.env.REACT_APP_BACKEND); // Adjust the URL if needed
    console.log('Stop button clicked for row:', row);
  
    // Emit the stop event
    socket.emit('stop_process', { username: row.job_name });
  
    // Update the row to show PlayButton again
    const updatedRows = rows.map((r) =>
      r.id === row.id ? { ...r, job_button: false } : r
    );
    setRows(updatedRows);
  };
  
  const handleViewStatus = (row) => {
    if (row.job_type === 'File Crawling') {
      setViewStatus(row.job_name);
    } else if (row.job_type === 'Web Crawling') {
      setViewStatus(row.job_name);
    }
  }
  


  const [rows, setRows] = useState([]); // State to hold the rows of the DataGrid
  const [selectedRows, setSelectedRows] = useState([]); // State to hold selected row IDs

  const columns = [
    { field: 'id', headerName: 'ID', width: 90 },
    { 
      field: 'job_name', 
      headerName: 'Job name',
      width: 300,
      editable: false ,
    },
    {
      field: 'job_type',
      headerName: 'Job type',
      width: 160,
      editable: false ,
    },
    {
      field: 'job_url',
      headerName: 'Crawling URL',
      description: 'This column has a value getter and is not sortable.',
      sortable: false,
      width: 500,
      editable: false ,
    },
    {
      field: 'job_time',
      headerName: 'Crawling Time(seconds)',
      type: 'number',
      width: 200,
      editable: false ,
    },
    {
      field: 'job_button',
      headerName: 'Play',
      description: 'This column has a value getter and is not sortable.',
      sortable: false,
      width: 80,
      renderCell: (params) => (
        params.row.job_button ? (
          <StopButton onClick={() => handleStopButtonClick(params.row, rows, setRows)} />
        ) : (
          <PlayButton onClick={() => handlePlayButtonClick(params.row, rows, setRows)} />
        )
      ),
    },
    {
      field: 'job_view',
      headerName: 'Details',
      description: 'This column has a value getter and is not sortable.',
      sortable: false,
      width: 80,
      renderCell: (params) => (
        <Box onClick={() => handleViewStatus(params.row)}>
          <ConsoleDrawer />
        </Box>
      ),
    },
    // {
    //   field: 'job_edit_button',
    //   headerName: 'Edit',
    //   description: 'This column has a value getter and is not sortable.',
    //   sortable: false,
    //   width: 80,
    //   renderCell: (params) => (
    //     <IconButton aria-label="edit" size="large">
    //       <EditIcon fontSize="inherit" />
    //     </IconButton>
    //   ),
    // },
  ];

  useEffect(() => {
    const fetchJobData = async () => {
      try {
        const response = await axios.get(process.env.REACT_APP_BACKEND + '/get_jobs'); // Use the new API endpoint
        const combinedData = response.data; // Get the combined data from the response
        
        if (combinedData) {
          console.log("Fetched Data:", combinedData);
        } else {
          console.warn("Received empty data!");
        }

        // Assuming combinedData contains arrays of jobs in "web_files" and "file_files"
        const formattedRows = [];
        
        // Format the data from web_files
        combinedData.web_files.forEach((job, index) => {
          const firstKey = Object.keys(job)[0];
          formattedRows.push({
            id: formattedRows.length + 1,
            job_name: job[firstKey]['jobName'] || "Unknown", // Adjust based on your data structure
            job_type: job[firstKey]['crawlingType'] || "Unknown", // Assuming this is web data
            job_time: job[firstKey]['crawlingTime'] || "Unknown", // Set this based on your requirements
            job_button: job[firstKey]['jobName'] in job_status,
            job_url: job[firstKey]['url'] || "Unknown",
          });
        });

        // Format the data from file_files
        combinedData.file_files.forEach((job, index) => {
          const firstKey = Object.keys(job)[0];
          formattedRows.push({
            id: formattedRows.length + 1,
            job_name: job[firstKey]['jobName'] || "Unknown", // Adjust based on your data structure
            job_type: job[firstKey]['crawlingType'] || "Unknown", // Assuming this is web data
            job_time: job[firstKey]['crawlingTime'] || "Unknown", // Set this based on your requirements
            job_button: job[firstKey]['jobName'] in job_status,
            job_url: job[firstKey]['url'] || "Unknown",
          });
        });

        setRows(formattedRows);
      } catch (error) {
        console.error('Error fetching job data:', error);
      }
    };

    fetchJobData();

    // socket.on('console_output', (data) => {
    //   setOutput((prevOutput) => prevOutput + data + '\n');
    // });

    // return () => {
    //   socket.off('console_output'); // Clean up on component unmount
    // };
  }, []);

  const handleSelectionChange = (selectionModel) => {
    setSelectedRows(selectionModel);
  };

  // Handle delete button click
  const handleDelete = async () => {
    // Get the selected job details based on selectedRows
    const selectedJobs = selectedRows.map((rowId) => {
      return rows.find((row) => row.id === rowId); // Find the row data by ID
    });
  
    // Check if there are any selected jobs to delete
    if (selectedJobs.length === 0) {
      alert('No jobs selected to delete.');
      return;
    }
  
    // Make multiple API calls to delete the selected jobs
    try {
      const deletePromises = selectedJobs.map((job) => {
        const requestBody = {
          job_name: job?.job_name || 'Unknown',
          job_type: job?.job_type || 'Unknown',
        };
  
        // Make the API call to delete the job (replace 'your-api-endpoint' with the actual API URL)
        return axios.delete(`http://192.168.140.236:5000/delete_job`, { data: requestBody });
      });
  
      // Wait for all delete requests to complete
      const responses = await Promise.all(deletePromises);
  
      // Optional: Handle the response
      console.log('Delete responses:', responses);
  
      // Update the UI by removing the deleted jobs from the rows state
      const remainingRows = rows.filter((row) => !selectedRows.includes(row.id));
      setRows(remainingRows);
      setSelectedRows([]); // Clear the selected rows
  
      alert('Selected jobs deleted successfully!');
    } catch (error) {
      console.error('Error deleting jobs:', error);
      alert('Failed to delete jobs.');
    }
  };


  const ref = useRef(null);
  const [fixedWidth, setFixedWidth] = useState('auto'); // Initial width

  useEffect(() => {
    // Measure the width after the component mounts
    if (ref.current) {
      setFixedWidth(ref.current.offsetWidth); // Get the current width
    }
  }, []);
  

  // const [s, setS] = useState(0)

  // const updateS = useCallback(() => {
  //   if (s !== window.innerWidth) {
  //     setS(window.innerWidth)
  //   }
  // }, [s])

  // useLayoutEffect(() => {
  //   window.addEventListener('resize', updateS)
  //   return () => window.removeEventListener('resize', updateS)
  // }, [updateS])

  return (
    <Box>
        <Box>
          <Grid container spacing={2}>
            <Grid size={2}>
              <ContentTitle pathname="  Crawling Job list" />
            </Grid>
            <Grid size={8}>
              
            </Grid>
            <Grid size={1}>
              <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'center',  // Horizontal centering
                alignItems: 'center',      // Vertical centering
                height: '100%'             // Make sure the box takes the full height of the grid item
              }}
              >
                <AddJobModal />
                {/* <Button variant="contained" sx={{ textTransform: 'none' }}>Add Job</Button> */}
              </Box>
            </Grid>
            <Grid size={1}>
              <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'center',  // Horizontal centering
                alignItems: 'center',      // Vertical centering
                height: '100%'             // Make sure the box takes the full height of the grid item
              }}
              >
                <Button variant="outlined" 
                        startIcon={<DeleteIcon />} 
                        disabled={selectedRows.length === 0} // Disable if no rows are selected
                        onClick={handleDelete} // Handle delete click
                >
                  Delete
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>
      <Box
          sx={{
            // display: 'flex',
            // justifyContent: 'center', // Center horizontally
            // alignItems: 'center', // Center vertically
          //   // height: '100vh', // Full viewport height for demonstration
          // //   // backgroundColor: 'lightgray',
          }}
          >
          <Box

            ref={ref}
            sx={{
              width: `${fixedWidth}px`, // Set the width to the measured width
              padding: '16px',
              boxSizing: 'border-box',
            }}        
          >
            {/* <div style={{ height: 350, width: '100%' }}>
              <Grid container spacing={2}>
                <Grid size={12}>
                  <MyComponent />
                </Grid>
              </Grid>
            </div> */}
            {/* <Box sx={{ flex: 1, position: 'relative' }}> */}
            {/* <Box sx={{ position: 'absolute', inset: 0 }}> */}
            <DataGrid
              // key={s}
              // sx={{ flexGrow: 1 }}
              rows={rows}
              columns={columns}
              initialState={{
                pagination: {
                  paginationModel: {
                    pjob_timeSize: 5,
                  },
                },
              }}
              onRowSelectionModelChange={(newSelection) => handleSelectionChange(newSelection)} // Change prop name
              pjob_timeSizeOptions={[5]}
              checkboxSelection
              disableRowSelectionOnClick
              // autoWidth
            />
            {/* </Box> */}
            {/* </Box> */}
          </Box>
      </Box>
    </Box>
  );
}
