import * as React from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionActions from '@mui/material/AccordionActions';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid2';
import ContentTitle from './ContentTitle';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import ConsoleOutput_log from './ConsoleOutput_log';

export default function CrawlingHistory() {

  const [logData, setLogData] = React.useState({});

  // Fetch log data from the Flask API
  React.useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch(process.env.REACT_APP_BACKEND + '/get_logs'); // Update URL if needed
        const data = await response.json();
        setLogData(data);
      } catch (error) {
        console.error('Error fetching log data:', error);
      }
    };

    fetchLogs();
  }, []);

  return (
    <Box>
      <Box>
        <Grid container spacing={2}>
          <Grid item xs={2}>
            <ContentTitle pathname="Crawling History" />
          </Grid>
          <Grid item xs={9}>
            {/* Additional content can go here */}
          </Grid>
          <Grid item xs={1}>
            {/* Any additional buttons or controls can go here */}
          </Grid>
        </Grid>
      </Box>

      <div>
        {Object.keys(logData).length > 0 ? (
          Object.entries(logData).map(([filename, content]) => (
            <Accordion key={filename}>
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls={`${filename}-content`}
                id={`${filename}-header`}
              >
                {filename}
              </AccordionSummary>
              <AccordionDetails>
                <Box>
                  <Grid container spacing={2}>
                    <Grid item xs={12} width={'100%'}>
                      <ConsoleOutput_log content={content} /> {/* Pass content to ConsoleOutput_log */}
                    </Grid>
                  </Grid>
                </Box>
              </AccordionDetails>
              <AccordionActions>
                <Button>Cancel</Button>
                <Button>Agree</Button>
              </AccordionActions>
            </Accordion>
          ))
        ) : (
          <p>No log data available.</p> // Message for empty data
        )}
      </div>
    </Box>
  );
}