import React, { useEffect, useState } from 'react';
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

import axios from 'axios';
import ConsoleOutput from './ConsoleOutput';


const thumbnail_type_list = [
  {
    value: 'PNG',
    label: 'PNG',
  },
  {
    value: 'JEPG',
    label: 'JEPG',
  },
  {
    value: 'BMP',
    label: 'BMP',
  },
];

export default function CrawlingSetting() {

  const [thumbnailURL, setThumbnailURL] = useState('');
  const [thumbnailType, setThumbnailType] = useState('PNG');

  // State for Elasticsearch Settings
  const [elasticsearchURL, setElasticsearchURL] = useState('');
  const [elasticsearchFingerprint, setElasticsearchFingerprint] = useState('');
  const [elasticsearchUsername, setElasticsearchUsername] = useState('');
  const [elasticsearchPassword, setElasticsearchPassword] = useState(''); 

  // State for Embedding Server Settings
  const [textEmbeddingURL, setTextEmbeddingURL] = useState('');
  const [imageEmbeddingURL, setImageEmbeddingURL] = useState('');

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await axios.get(process.env.REACT_APP_BACKEND + '/get_setting');
        const settings = response.data.other_files;

        settings.forEach((setting) => {
          if (setting['elasticsearch.yaml']) {
            const es = setting['elasticsearch.yaml'];
            setElasticsearchURL(es.elasticsearch_url);
            setElasticsearchFingerprint(es.elasticsearch_fingerprint);
            setElasticsearchUsername(es.elasticsearch_username);
            setElasticsearchPassword(es.elasticsearch_password);
          }
          if (setting['embedding.yaml']) {
            const embedding = setting['embedding.yaml'];
            setTextEmbeddingURL(embedding.textembedding_url);
            setImageEmbeddingURL(embedding.imageembedding_url);
          }
          if (setting['thumbnail.yaml']) {
            const thumbnail = setting['thumbnail.yaml'];
            setThumbnailURL(thumbnail.thumbnail_url);
            setThumbnailType(thumbnail.thumbnail_type);
          }
        });
      } catch (error) {
        console.log('Error fetching settings:', error);
      }
    };

    fetchSettings();
  }, []);


  // Handle Submit for Thumbnail Settings
  const handleThumbnailSubmit = async () => {
    try {
      const data = {
        thumbnail_url: thumbnailURL,
        thumbnail_type: thumbnailType,
      };
      const response = await axios.post(process.env.REACT_APP_BACKEND + '/set_setting', data, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      alert(response.data.message);
    } catch (error) {
      console.error('Error submitting Thumbnail Settings:', error);
      alert('Failed to submit Thumbnail Settings');
    }
  };

  // Handle Submit for Elasticsearch Settings
  const handleElasticsearchSubmit = async () => {
    try {
      const data = {
        elasticsearch_url: elasticsearchURL,
        elasticsearch_fingerprint: elasticsearchFingerprint,
        elasticsearch_username: elasticsearchUsername,
        elasticsearch_password: elasticsearchPassword,
      };
      const response = await axios.post(process.env.REACT_APP_BACKEND + '/set_setting', data, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      alert(response.data.message);
    } catch (error) {
      console.error('Error submitting Elasticsearch Settings:', error);
      alert('Failed to submit Elasticsearch Settings');
    }
  };

  // Handle Submit for Embedding Server Settings
  const handleEmbeddingSubmit = async () => {
    try {
      const data = {
        textembedding_url: textEmbeddingURL,
        imageembedding_url: imageEmbeddingURL,
      };
      const response = await axios.post(process.env.REACT_APP_BACKEND + '/set_setting', data, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      alert(response.data.message);
    } catch (error) {
      console.error('Error submitting Embedding Server Settings:', error);
      alert('Failed to submit Embedding Server Settings');
    }
  };

  return (
    <Box>
      <Box>
        <Grid container spacing={2}>
          <Grid item xs={2}>
            <ContentTitle pathname="Crawling Setting" />
          </Grid>
          <Grid item xs={9}>
            {/* You can add additional content here if needed */}
          </Grid>
          <Grid item xs={1}>
            {/* Additional Grid Item if needed */}
          </Grid>
        </Grid>
      </Box>

      <div>
        {/* Thumbnail Setting Accordion */}
        <Accordion defaultExpanded>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="thumbnail-content"
            id="thumbnail-header"
          >
            Thumbnail Setting
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Grid container spacing={2}>
                <Grid item size={{ xs: 12, sm: 12, lg: 3 }}>
                  <TextField
                    id="thumbnail-url"
                    label="URL"
                    fullWidth
                    value={thumbnailURL}
                    onChange={(e) => setThumbnailURL(e.target.value)}
                    helperText="Input Thumbnail URL"
                  />
                </Grid>
                <Grid item size={{ xs: 12, sm: 12, lg: 3 }}>
                  <TextField
                    id="thumbnail-type"
                    select
                    fullWidth
                    label="Thumbnail Type"
                    value={thumbnailType}
                    onChange={(e) => setThumbnailType(e.target.value)}
                    helperText="Select Thumbnail Type"
                  >
                    {thumbnail_type_list.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
              </Grid>
            </Box>
          </AccordionDetails>
          <AccordionActions>
            <Button
              variant="outlined"
              color="secondary"
              onClick={() => {
                // Optionally, reset fields or perform other actions
              }}
            >
              Cancel
            </Button>
            <Button variant="contained" color="primary" onClick={handleThumbnailSubmit}>
              Agree
            </Button>
          </AccordionActions>
        </Accordion>

        {/* Elasticsearch Setting Accordion */}
        <Accordion defaultExpanded>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="elasticsearch-content"
            id="elasticsearch-header"
          >
            Elasticsearch Setting
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Grid container spacing={2}>
                <Grid item size={{ xs: 12, sm: 12, lg: 3 }}>
                  <TextField
                    id="elasticsearch-url"
                    label="Elasticsearch URL"
                    fullWidth
                    value={elasticsearchURL}
                    onChange={(e) => setElasticsearchURL(e.target.value)}
                    helperText="Input Elasticsearch URL"
                  />
                </Grid>
                <Grid item size={{ xs: 12, sm: 12, lg: 3 }}>
                  <TextField
                    id="elasticsearch-fingerprint"
                    label="Elasticsearch Fingerprint"
                    fullWidth
                    value={elasticsearchFingerprint}
                    onChange={(e) => setElasticsearchFingerprint(e.target.value)}
                    helperText="Input Elasticsearch Fingerprint"
                  />
                </Grid>
                <Grid item size={{ xs: 12, sm: 12, lg: 3 }}>
                  <TextField
                    id="elasticsearch-username"
                    label="Elasticsearch Username"
                    fullWidth
                    value={elasticsearchUsername}
                    onChange={(e) => setElasticsearchUsername(e.target.value)}
                    helperText="Input Elasticsearch Username"
                  />
                </Grid>
                <Grid item size={{ xs: 12, sm: 12, lg: 3 }}>
                  <TextField
                    id="elasticsearch-password"
                    label="Elasticsearch Password"
                    type="password"
                    fullWidth
                    value={elasticsearchPassword}
                    onChange={(e) => setElasticsearchPassword(e.target.value)}
                    helperText="Input Elasticsearch Password"
                  />
                </Grid>
              </Grid>
            </Box>
          </AccordionDetails>
          <AccordionActions>
            <Button
              variant="outlined"
              color="secondary"
              onClick={() => {
                // Optionally, reset fields or perform other actions
              }}
            >
              Cancel
            </Button>
            <Button variant="contained" color="primary" onClick={handleElasticsearchSubmit}>
              Agree
            </Button>
          </AccordionActions>
        </Accordion>

        {/* Embedding Server Setting Accordion */}
        <Accordion defaultExpanded>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="embedding-content"
            id="embedding-header"
          >
            Embedding Server Setting
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              <Grid container spacing={2}>
                <Grid item size={{ xs: 12, sm: 12, lg: 3 }}>
                  <TextField
                    id="text-embedding-url"
                    label="Text Embedding URL"
                    fullWidth
                    value={textEmbeddingURL}
                    onChange={(e) => setTextEmbeddingURL(e.target.value)}
                    helperText="Input Text Embedding URL"
                  />
                </Grid>
                <Grid item size={{ xs: 12, sm: 12, lg: 3 }}>
                  <TextField
                    id="image-embedding-url"
                    label="Image Embedding URL"
                    fullWidth
                    value={imageEmbeddingURL}
                    onChange={(e) => setImageEmbeddingURL(e.target.value)}
                    helperText="Input Image Embedding URL"
                  />
                </Grid>
              </Grid>
            </Box>
          </AccordionDetails>
          <AccordionActions>
            <Button
              variant="outlined"
              color="secondary"
              onClick={() => {
                // Optionally, reset fields or perform other actions
              }}
            >
              Cancel
            </Button>
            <Button variant="contained" color="primary" onClick={handleEmbeddingSubmit}>
              Agree
            </Button>
          </AccordionActions>
        </Accordion>
      </div>
    </Box>
  );
}
