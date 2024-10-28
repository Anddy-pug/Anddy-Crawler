import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import { useJobContext } from '../context/JobContext';

const webContentsTypes = [
  { value: 'Static Web Contents', label: 'Static Web Contents' },
  { value: 'Dynamic Web Contents', label: 'Dynamic Web Contents' },
  { value: 'NextCloud', label: 'NextCloud' },
  { value: 'OpenProject', label: 'OpenProject' },
];

export default function AddJobModalWeb() {
  const { jobData, setJobData } = useJobContext();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setJobData((prevData) => {
      const newData = { ...prevData, [name]: value };

      // Automatically set loginRequired for NextCloud, TestRail, OpenProject
      if (name === 'webContentsType' && ['NextCloud', 'OpenProject'].includes(value)) {
        newData.loginRequired = 'Required';
      }

      return newData;
    });
  };

  return (
    <Box>
      <Grid container spacing={2}>
        {/* Crawling Web Contents Type */}
        <Grid size={12}>
          <TextField
            id="web-contents-type"
            select
            fullWidth
            label="Crawling Web Contents Type"
            name="webContentsType"
            helperText="Please select your web content type"
            value={jobData.webContentsType || 'Static Web Contents'}
            onChange={handleInputChange}
          >
            {webContentsTypes.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>
        </Grid>

        {/* Crawling Time */}
        <Grid size={12}>
          <TextField
            id="crawling-time"
            label="Time"
            fullWidth
            name="crawlingTime"
            helperText="Input crawling time"
            value={jobData.crawlingTime || ''}
            onChange={handleInputChange}
          />
        </Grid>

        {/* Login Required */}
        <Grid size={12}>
          <TextField
            id="login-required"
            select
            fullWidth
            label="Login"
            name="loginRequired"
            helperText="Login required or not"
            value={jobData.loginRequired || 'Not Required'}
            disabled={['NextCloud', 'OpenProject'].includes(jobData.webContentsType)} // Disable when auto-selected
            onChange={handleInputChange}
          >
            <MenuItem value="Required">Required</MenuItem>
            <MenuItem value="Not Required">Not Required</MenuItem>
          </TextField>
        </Grid>

        {/* Conditional Rendering of LoginContents */}
        {(jobData.loginRequired === 'Required') && (
          <LoginContents
            disabledFields={
              ['NextCloud', 'OpenProject'].includes(jobData.webContentsType)
                ? ['usernameId', 'passwordId', 'submitId', 'logout_url']
                : [] // Don't disable any fields for other content types like Static or Dynamic Web Contents
            }
          />
        )}
      </Grid>
    </Box>
  );
}

export function LoginContents({ disabledFields = [] }) {
  const { jobData, setJobData } = useJobContext();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setJobData((prevData) => ({ ...prevData, [name]: value }));
  };

  const isDisabled = (field) => disabledFields.includes(field);

  return (
    <Box>
      <Grid container spacing={2}>
        {/* Login URL */}
        <Grid size={12}>
          <TextField
            id="login_url"
            label="Login URL"
            fullWidth
            name="login_url"
            helperText="Input Login URL"
            value={jobData.login_url || ''}
            onChange={handleInputChange}
            disabled={isDisabled('login_url')}
          />
        </Grid>

        {/* Logout URL */}
        <Grid size={12}>
          <TextField
            id="logout_url"
            label="Logout URL"
            fullWidth
            name="logout_url"
            helperText="Input Logout URL"
            value={jobData.logout_url || ''}
            onChange={handleInputChange}
            disabled={isDisabled('logout_url')}
          />
        </Grid>

        {/* Username */}
        <Grid size={12}>
          <TextField
            id="username"
            label="Username"
            fullWidth
            name="username"
            helperText="Input Username"
            value={jobData.username || ''}
            onChange={handleInputChange}
            disabled={isDisabled('username')}
          />
        </Grid>

        {/* Password */}
        <Grid size={12}>
          <TextField
            id="password"
            type="password"
            label="Password"
            fullWidth
            name="password"
            helperText="Input Password"
            value={jobData.password || ''}
            onChange={handleInputChange}
            disabled={isDisabled('password')}
          />
        </Grid>

        {/* Username ID */}
        <Grid size={12}>
          <TextField
            id="username-id"
            label="Username ID"
            fullWidth
            name="usernameId"
            helperText="Input Username ID"
            value={jobData.usernameId || ''}
            onChange={handleInputChange}
            disabled={isDisabled('usernameId')}
          />
        </Grid>

        {/* Password ID */}
        <Grid size={12}>
          <TextField
            id="password-id"
            type="password"
            label="Password ID"
            fullWidth
            name="passwordId"
            helperText="Input Password ID"
            value={jobData.passwordId || ''}
            onChange={handleInputChange}
            disabled={isDisabled('passwordId')}
          />
        </Grid>

        {/* Submit Button ID */}
        <Grid size={12}>
          <TextField
            id="submit-id"
            label="Submit ID"
            fullWidth
            name="submitId"
            helperText="Input Submit Button ID"
            value={jobData.submitId || ''}
            onChange={handleInputChange}
            disabled={isDisabled('submitId')}
          />
        </Grid>
      </Grid>
    </Box>
  );
}
