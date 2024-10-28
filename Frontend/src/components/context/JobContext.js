// JobContext.js
import React, { createContext, useContext, useState } from 'react';

const JobContext = createContext();

export const useJobContext = () => {
  return useContext(JobContext);
};

export const JobProvider = ({ children }) => {
  const [jobData, setJobData] = useState({
    jobName: '',
    crawlingType: 'File Crawling',
    url: '',
    indexName: '',
    webContentsType: 'Static Web Contents',
    crawlingTime: '',
    loginRequired: 'Not Required',
    username: '',
    password: '',
    usernameId: '',
    passwordId: '',
    submitId: '',
    etc: '',
    login_url: '',
    logout_url: '',
  });

  const [viewStatus, setViewStatus] = useState(''); // Another shared variable

  return (
    <JobContext.Provider value={{ jobData, setJobData, viewStatus, setViewStatus}}>
      {children}
    </JobContext.Provider>
  );
};
