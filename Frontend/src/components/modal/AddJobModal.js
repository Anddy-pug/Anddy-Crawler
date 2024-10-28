import React, { useState } from 'react';
import Button from '@mui/material/Button';
import { styled } from '@mui/material/styles';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import Typography from '@mui/material/Typography';
import { Box} from '@mui/material';
import Grid from '@mui/material/Grid2';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import AddJobModalFile from './AddJobModalFile';
import AddJobModalWeb from './AddJobModalWeb';
import { useJobContext  } from '../context/JobContext';

const BootstrapDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiDialogContent-root': {
    padding: theme.spacing(2),
  },
  '& .MuiDialogActions-root': {
    padding: theme.spacing(1),
  },
}));

const crawlingTypes = [
    {
      value: 'File Crawling',
      label: 'File Crawling',
    },
    {
      value: 'Web Crawling',
      label: 'Web Crawling',
    },
  ];

export default function AddJobModal() {

  const { jobData, setJobData } = useJobContext();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setJobData((prevData) => ({ ...prevData, [name]: value }));
  };

  const [open, setOpen] = React.useState(false);

  const handleSubmit = () => {

    // Send data to the backend
    fetch(process.env.REACT_APP_BACKEND + '/set_job', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(jobData),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log('Success:', data);
            setOpen(false);  // Close modal on success
        })
        .catch((error) => console.error('Error:', error));
    handleClose();
  };

  const handleClickOpen = () => {
    setOpen(true);
  };
  const handleClose = () => {
    setOpen(false);
  };

  return (
    <React.Fragment>
      <Button variant="outlined" onClick={handleClickOpen}>
        Add Job
      </Button>
      <BootstrapDialog
        onClose={handleClose}
        aria-labelledby="customized-dialog-title"
        open={open}
      >
        <DialogTitle sx={{ m: 0, p: 2 }} id="customized-dialog-title">
          Add Crawling Job
        </DialogTitle>
        <IconButton
          aria-label="close"
          onClick={handleClose}
          sx={(theme) => ({
            position: 'absolute',
            right: 8,
            top: 8,
            color: theme.palette.grey[500],
          })}
        >
          <CloseIcon />
        </IconButton>
        <DialogContent dividers>
          <Box>
          <Grid container spacing={2}>
              <Grid size={12}>
                <TextField
                  id="job-name"
                  fullWidth
                  label="Job Name"
                  name="jobName" // Added name attribute
                  helperText="Input crawling job name"
                  value={jobData.jobName || ''}
                  onChange={handleInputChange}
                />
              </Grid>
              <Grid size={12}>
                <TextField
                  id="crawling-type"
                  select
                  fullWidth
                  label="Crawling Type"
                  name="crawlingType" // Added name attribute
                  helperText="Select crawling type"
                  value={jobData.crawlingType || 'File Crawling'}
                  onChange={handleInputChange} // Use handleInputChange directly
                >
                  {crawlingTypes.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid size={12}>
                <TextField
                  id="url"
                  fullWidth
                  label="URL"
                  name="url" // Added name attribute
                  helperText="Input crawling URL"
                  value={jobData.url || ''}
                  onChange={handleInputChange}
                />
              </Grid>
              <Grid size={12}>
                <TextField
                  id="index-name"
                  fullWidth
                  label="Index Name"
                  name="indexName" // Added name attribute
                  helperText="Input Elastic index"
                  value={jobData.indexName || ''}
                  onChange={handleInputChange}
                />
              </Grid>
              <Grid size={12}>
                <TextField
                  id="etc"
                  fullWidth
                  label="etc"
                  name="etc" // Added name attribute
                  helperText="Input other info"
                  value={jobData.etc || ''}
                  onChange={handleInputChange}
                />
              </Grid>
              {jobData.crawlingType === "Web Crawling" && (
                <AddJobModalWeb />
              )}
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button autoFocus onClick={handleSubmit}>
            Add Job
          </Button>
        </DialogActions>
      </BootstrapDialog>
    </React.Fragment>
  );
}
