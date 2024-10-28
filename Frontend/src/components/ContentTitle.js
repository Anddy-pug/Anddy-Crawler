import * as React from 'react';
import Box from '@mui/material/Box';
import { DataGrid } from '@mui/x-data-grid';
import PlayButton from './table_components/buttons/PlayButton';
import Stack from '@mui/material/Stack';
import CircularProgress from '@mui/material/CircularProgress';
import Chip from '@mui/material/Chip';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid2';
import Typography from '@mui/material/Typography';
import PropTypes from 'prop-types';
import AddJobModal from './modal/AddJobModal';


ContentTitle.propTypes = {
    pathname: PropTypes.string.isRequired,
  };

export default function ContentTitle({ pathname }) {
    return (
      <Box
        sx={{
          py: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'left',
          textAlign: 'left',
        }}
      >
        <Typography>{pathname}</Typography>
      </Box>
    );
  }