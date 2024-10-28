import * as React from 'react';
import PropTypes from 'prop-types';
import { Box, CssBaseline } from '@mui/material';
import { createTheme, ThemeProvider, useTheme } from '@mui/material/styles';
import { AppProvider } from '@toolpad/core/AppProvider';
import { DashboardLayout } from '@toolpad/core/DashboardLayout';
import JobList from './JobList';
import Setting from './CrawlingSetting';
import CrawlingHistory from './CrawlingHistory';
import { JobProvider } from './context/JobContext';
import logo from './../favicon.svg';
import "../assets/styles/style.css";
import { Routes, Route } from 'react-router-dom';

function MainDashboard(props) {
  const { window } = props;
  const demoWindow = window !== undefined ? window() : undefined;

  // State to manage and toggle theme mode
  const [mode, setMode] = React.useState('light');
  const toggleTheme = () => setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));

  // Create theme based on current mode
  const theme = React.useMemo(() =>
    createTheme({
      palette: {
        mode: mode,
      },
    }), [mode]
  );

  const demoTheme = createTheme({
    cssVariables: {
      colorSchemeSelector: 'data-toolpad-color-scheme',
    },
    colorSchemes: { light: true, dark: true },
    breakpoints: {
      values: {
        xs: 0,
        sm: 600,
        md: 600,
        lg: 1200,
        xl: 1536,
      },
    },
  });

  const iconColor = theme.palette.mode === 'dark' ? '#ffffff' : '#000000';

  const NAVIGATION = [
    {
      kind: 'header',
      title: 'Main items',
    },
    {
      segment: 'joblist',
      title: 'Crawling Job list',
      icon: <span className="material-symbols-outlined" style={{ color: iconColor }}>list</span>,
    },
    {
      segment: 'setting',
      title: 'Crawling Setting',
      icon: <span className="material-symbols-outlined" style={{ color: iconColor }}>settings</span>,
    },
    {
      kind: 'divider',
    },
    {
      kind: 'header',
      title: 'Analytics',
    },
    {
      segment: 'integrations',
      title: 'Crawling History',
      icon: <span className="material-symbols-outlined" style={{ color: iconColor }}>history</span>,
    },
  ];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppProvider
        navigation={NAVIGATION}
        theme={theme} // Ensure theme is passed
        window={demoWindow}
        branding={{
          logo: <img src={logo} alt="MUI logo" />,
          title: 'Advanced Crawler',
        }}
      >
        <JobProvider>
          <DashboardLayout>
            <Box sx={{ width: '100%', paddingX: 2 }}>
              {/* <button onClick={toggleTheme}>
                Toggle to {mode === 'light' ? 'Dark' : 'Light'} Mode
              </button> */}
              <Routes>
                <Route path="/" element={<JobList />} />
                <Route path="/joblist" element={<JobList />} />
                <Route path="/setting" element={<Setting />} />
                <Route path="/integrations" element={<CrawlingHistory />} />
                <Route path="*" element={<h1>404 - Page Not Found</h1>} />
              </Routes>
            </Box>
          </DashboardLayout>
        </JobProvider>
      </AppProvider>
    </ThemeProvider>
  );
}

MainDashboard.propTypes = {
  window: PropTypes.func,
};

export default MainDashboard;




