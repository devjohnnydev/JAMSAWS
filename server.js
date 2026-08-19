const express = require('express');
const path = require('path');
const fs = require('fs');
const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from jams-timer directory
app.use(express.static(path.join(__dirname, 'jams-timer')));

// API endpoint to load real Jams from the catalog JSON file
app.get('/api/jams', (req, res) => {
  const filePath = path.join(__dirname, 'global_static_answer_challenges.json');
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: 'Catalog file not found' });
  }

  try {
    const rawData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const uniqueMap = new Map();

    rawData.forEach(item => {
      if (!item.task || !item.task.title) return;
      const key = `${item.challengeId}_${item.task.title}`;
      if (!uniqueMap.has(key)) {
        // Classify difficulty based on keywords in title/content
        let type = 'medium';
        const title = item.task.title.toLowerCase();
        const content = (item.task.content || '').toLowerCase();

        if (title.includes('leak') || title.includes('import') || title.includes('first') || title.includes('breach')) {
          type = 'easy';
        } else if (title.includes('optimization') || title.includes('hog') || title.includes('underwriting') || title.includes('fraud') || title.includes('pipeline') || content.includes('performanc') || content.includes('recursao')) {
          type = 'hard';
        }

        uniqueMap.set(key, {
          id: item.challengeId + '_' + item.task.taskNumber,
          type: type,
          name: `${item.task.title} [${item.challengeId}]`,
          content: item.task.content || '',
          validationCode: item.task.validationFunction || '',
          validationType: item.task.validationType || '',
          runtime: item.task.validationFunctionRuntime || ''
        });
      }
    });

    res.json(Array.from(uniqueMap.values()));
  } catch (error) {
    res.status(500).json({ error: 'Failed to parse Jams catalog', details: error.message });
  }
});

// Serve index.html for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'jams-timer', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
