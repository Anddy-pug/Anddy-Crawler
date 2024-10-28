import * as React from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Grid from '@mui/material/Grid2';
import MenuItem from '@mui/material/MenuItem';

const currencies = [
    {
      value: 'Static Web Contents',
      label: 'Static Web Contents',
    },
    {
      value: 'Dynamic Web Contents',
      label: 'Dynamic Web Contents',
    },
    {
      value: 'NextCloud',
      label: 'NextCloud',
    },
    {
      value: 'TestRail',
      label: 'TestRail',
    },
    {
      value: 'OpenProject',
      label: 'OpenProject',
    },
];

export default function AddJobModalFile() {
  return (
    <Box>
        <Grid container spacing={2}>
            <Grid size={12}>
                <TextField
                    id="outlined-select-currency"
                    select
                    label="Select"
                    defaultValue="EUR"
                    helperText="Please select your currency"
                    >
                    {currencies.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                        {option.label}
                        </MenuItem>
                    ))}
                </TextField>
            </Grid>
            <Grid size={12}>
                <TextField
                    id="outlined-helperText"
                    label="URL"
                    defaultValue=""
                    helperText="input crawling URL"
                />
            </Grid>
            <Grid size={12}>
                <TextField
                    id="outlined-helperText"
                    label="Index Name"
                    defaultValue=""
                    helperText="input elastic index"
                />
            </Grid>
            <Grid size={12}>

            </Grid>
        </Grid>
    </Box>
  );
}
