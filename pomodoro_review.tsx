/*
 * File: pomodoro_review.tsx
 * Description: Front-end React component for reviewing pomodoro entries with AI-generated summaries.
 * Parameters: None (client-side component).
 * Inputs: Loads `pomodoro.txt` from server or local storage, parses timestamped entries.
 * Processing: Parses entries, groups by date/year/month, renders overview, allows AI summary generation via Google Gemini API, saves AI logs.
 * Outputs: Renders interactive UI with entry lists, date navigation, AI summary display, and downloadable AI log.
 */
import React, { useState, useEffect } from 'react';
import { Clock, Calendar, ArrowLeft, Upload, AlertCircle, Sparkles, Key, X } from 'lucide-react';
import { marked } from 'marked';

interface Entry {
  timestamp: string;
  tag: string;
  note: string;
}

type GroupedDates = {
  [year: string]: {
    [month: string]: string[];
  };
};

type Summaries = {
  [date: string]: string;
};

const TimeTracker = () => {
  // --- Application State ---
  const [entries, setEntries] = useState<Entry[]>([]); // Array of parsed pomodoro entries
  const [view, setView] = useState<string>('loading'); // Current active view: 'loading', 'upload', 'overview', 'details', 'all'
  const [dates, setDates] = useState<string[]>([]); // Array of unique date strings (YYYY-MM-DD)
  const [groupedDates, setGroupedDates] = useState<GroupedDates>({}); // Dates grouped by Year and Month for hierarchical navigation
  const [selectedDate, setSelectedDate] = useState<string | null>(null); // The date selected by the user for detailed review
  const [loadingError, setLoadingError] = useState<string | null>(null); // Stores any errors encountered during file loading

  // --- Gemini AI State ---
  const [apiKey, setApiKey] = useState<string>(localStorage.getItem('gemini_api_key') || ''); // API key for Google Gemini
  const [showKeyInput, setShowKeyInput] = useState<boolean>(false); // Controls visibility of the API key input modal
  const [isGenerating, setIsGenerating] = useState<boolean>(false); // Indicates if an AI summary is currently being generated
  const [summaries, setSummaries] = useState<Summaries>({}); // Dictionary of cached summaries keyed by date string (e.g., {'January 1, 2024': 'Summary text'})

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (entries.length > 0) {
      extractAndGroupDates();
      // Determine initial view if not already set or invalid
      if (view === 'loading' || view === 'upload') {
        setView('overview');
      }
    } else if (view !== 'loading') {
      if (view !== 'upload') setView('upload');
    }
  }, [entries]);

  const saveApiKey = (key: string) => {
    setApiKey(key);
    localStorage.setItem('gemini_api_key', key);
    setShowKeyInput(false);
  };

  /**
   * Loads data from localStorage cache and attempts to fetch fresh data from 'pomodoro.txt'.
   */
  const loadData = async () => {
    // 1. Load AI summaries from cache
    const cachedSummaries = localStorage.getItem('pomodoro_summaries');
    if (cachedSummaries) {
      try {
        setSummaries(JSON.parse(cachedSummaries));
      } catch (e) {
        console.error("Failed to parse cached summaries", e);
      }
    }

    // 2. Try loading pomodoro data from localStorage cache first
    const cachedData = localStorage.getItem('pomodoro_data');
    if (cachedData) {
      parseFileContent(cachedData);
    }

    // 3. Attempt to fetch fresh pomodoro data from the server
    try {
      const response = await fetch('pomodoro.txt');
      if (response.ok) {
        const text = await response.text();
        // Only trigger update if content has changed
        if (text !== cachedData) {
          localStorage.setItem('pomodoro_data', text);
          parseFileContent(text);
        }
      } else {
        if (!cachedData) throw new Error('File not found');
      }
    } catch (error) {
      console.log('Auto-load failed', error);
      if (!cachedData) {
        setLoadingError('Could not load pomodoro.txt and no cache found.');
        setView('upload');
      }
    }
  };

  /**
   * Extracts unique dates from entries and organizes them into a hierarchical structure (Year -> Month -> Dates).
   */
  const extractAndGroupDates = () => {
    const uniqueDates = [...new Set(entries.map((entry: Entry) => {
      const date = new Date(entry.timestamp);
      return date.toISOString().split('T')[0];
    }))].sort().reverse();

    setDates(uniqueDates);

    const grouped: GroupedDates = {};
    uniqueDates.forEach(date => {
      const dateObj = new Date(date);
      const year = dateObj.getFullYear().toString();
      const month = dateObj.toLocaleString('en-US', { month: 'long' });

      if (!grouped[year]) {
        grouped[year] = {};
      }
      if (!grouped[year][month]) {
        grouped[year][month] = [];
      }
      grouped[year][month].push(date);
    });

    setGroupedDates(grouped);
  };

  /**
   * Parses a single line from the pomodoro file using regex.
   * Expected format: [YYYY-MM-DD HH:MM:SS] (tag) note content
   */
  const parseEntry = (line: string): Entry | null => {
    const regex = /\[(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\]\s*\(([^)]*)\):\s*(.+)/;
    const match = line.match(regex);

    if (match) {
      const [, datePart, timePart, tag, note] = match;
      const timestamp = `${datePart}T${timePart}`;
      return {
        timestamp: new Date(timestamp).toISOString(),
        tag: tag.trim(),
        note: note.trim()
      };
    }
    return null;
  };

  /**
   * Splits multi-line text into lines, parses each, and updates state.
   */
  const parseFileContent = (text: string) => {
    const lines = text.split('\n').filter(line => line.trim());
    const parsedEntries = lines
      .map(line => parseEntry(line))
      .filter((entry): entry is Entry => entry !== null);

    setEntries(parsedEntries);
  };

  const saveToAiLog = (dateStr: string, summaryText: string) => {
    const separator = "\n\n---\n\n";
    const newEntry = `Date: ${dateStr}\n\n${summaryText}${separator}`;

    // Get existing log or start empty
    let currentLog = localStorage.getItem('pomodoro_ai_log') || "";

    // Avoid rewriting if it looks like the last entry is the same (simple check)
    if (!currentLog.includes(newEntry.trim())) {
      currentLog += newEntry;
      localStorage.setItem('pomodoro_ai_log', currentLog);
      // downloadAiLog(currentLog);
    } else {
      // It exists, maybe just update the file anyway so user gets latest
      // downloadAiLog(currentLog);
    }
  };

  const downloadAiLog = async (content: string) => {
    // Clean content: remove excessive newlines (3 or more becomes 2)
    const cleanContent = content.replace(/\n{3,}/g, '\n\n');

    // Try to use the modern File System Access API to pick location
    if ((window as any).showSaveFilePicker) {
      try {
        const handle = await (window as any).showSaveFilePicker({
          suggestedName: 'pomodoro_ai.txt',
          types: [{
            description: 'Text File',
            accept: { 'text/plain': ['.txt'] },
          }],
        });
        const writable = await handle.createWritable();
        await writable.write(content);
        await writable.close();
        return; // Success
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          console.error('File access error:', err);
          alert('Could not save to chosen location. Falling back to default download.');
        } else {
          return; // User cancelled
        }
      }
    }

    // Fallback
    const blob = new Blob([cleanContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'pomodoro_ai.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // CONFIGURATION: Model and Prompt
  const AI_CONFIG = {
    model: "gemma-3-27b-it", // Updated to use the requested model
    basePrompt: `Analyze these time tracking entries and provide a concise summary of the day.
Focus on:
1. Key achievements (Work/Tasks completions).
2. Flow and consistency (disturbances, breaks).
3. Overall mood/productivity based on the notes.
Use professional but encouraging tone and provide points.`,
  };

  /**
   * Calls the Google Gemini API to generate a summary for a specific date's entries.
   * @param dateEntries An array of Entry objects for the selected date.
   * @param dateStr The date string (e.g., "January 1, 2024") for which to generate the summary.
   */
  const generateSummary = async (dateEntries: Entry[], dateStr: string) => {
    // Ensure API key is available
    if (!apiKey) {
      setShowKeyInput(true);
      return;
    }

    setIsGenerating(true);

    // Filter and format entries for the AI prompt
    const entriesText = dateEntries.map((e: Entry) =>
      `[${formatTime(e.timestamp)}] (${e.tag}): ${e.note}`
    ).join('\n');

    // Build the payload for the API request
    const prompt = `${AI_CONFIG.basePrompt}
    
    Date: ${dateStr}
    
    Entries:
    ${entriesText}`;

    try {
      // Make the API call to Google Gemini
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${AI_CONFIG.model}:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{
            parts: [{ text: prompt }]
          }]
        })
      });

      const data = await response.json();

      // Handle API errors
      if (data.error) {
        throw new Error(data.error.message);
      }

      // Extract the generated text from the response
      const text = data.candidates[0].content.parts[0].text;

      // Update summaries state and persist to localStorage
      const newSummaries = { ...summaries, [dateStr]: text };
      setSummaries(newSummaries);
      localStorage.setItem('pomodoro_summaries', JSON.stringify(newSummaries));

      // Append the new summary to the persistent AI log
      saveToAiLog(dateStr, text);

    } catch (error: any) {
      alert('Failed to generate summary: ' + (error.message || 'Unknown error'));
    } finally {
      setIsGenerating(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      localStorage.setItem('pomodoro_data', text);
      parseFileContent(text);
      setView('overview');
    } catch (error) {
      console.error('Error reading file:', error);
      alert('Error reading file. Please try again.');
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getEntriesForDate = (dateStr: string) => {
    return entries.filter((entry: Entry) => {
      const entryDate = new Date(entry.timestamp).toISOString().split('T')[0];
      return entryDate === dateStr;
    });
  };

  const handleDateSelect = (dateStr: string) => {
    setSelectedDate(dateStr);
    setView('details');
  };

  // Safe markdown renderer component
  const Markdown = ({ content }: { content: string }) => {
    return (
      <div className="prose prose-invert prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: marked.parse(content) }} />
    );
  };

  if (view === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-screen text-gray-400">
        <p>Loading entries...</p>
      </div>
    );
  }

  if (view === 'upload' && entries.length === 0) {
    return (
      <div className="max-w-4xl mx-auto p-4 bg-gray-900 min-h-screen">
        <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
          <h1 className="text-2xl font-bold mb-4 text-gray-100 flex items-center justify-center">
            <Clock className="w-7 h-7 mr-2" />
            Time Tracker Review
          </h1>

          {loadingError && (
            <div className="bg-red-900/50 border border-red-700 rounded-lg p-4 mb-4 text-red-200">
              <p>{loadingError}</p>
            </div>
          )}

          <div className="text-center mt-8">
            <Upload className="w-14 h-14 mx-auto mb-3 text-gray-500" />
            <p className="text-gray-400 mb-4">Upload your pomodoro.txt file</p>

            <label className="inline-block bg-blue-600 text-white py-2 px-5 rounded-lg hover:bg-blue-700 cursor-pointer font-medium">
              <input
                type="file"
                accept=".txt"
                onChange={handleFileUpload}
                className="hidden"
              />
              Choose File
            </label>
          </div>
        </div>
      </div>
    );
  }

  if (view === 'details' && selectedDate) {
    const dateEntries = getEntriesForDate(selectedDate);
    return (
      <div className="max-w-4xl mx-auto p-2 bg-gray-900 min-h-screen">
        <div className="bg-gray-800 rounded-lg shadow-lg p-3 border border-gray-700">
          <div className="flex justify-between items-center mb-3">
            <button
              onClick={() => { setSelectedDate(null); setView('overview'); }}
              className="flex items-center text-blue-400 hover:text-blue-300 text-sm"
            >
              <ArrowLeft className="w-4 h-4 mr-1" />
              Back to dates
            </button>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  if (confirm('Refresh data from server?')) {
                    loadData();
                  }
                }}
                className="text-gray-500 hover:text-gray-300 text-xs flex items-center"
                title="Reload Data"
              >
                <Clock className="w-3 h-3 mr-1" />
                Refresh
              </button>
              <button
                onClick={() => setShowKeyInput(true)}
                className="text-gray-500 hover:text-gray-300 text-xs flex items-center"
                title="Set API Key"
              >
                <Key className="w-3 h-3 mr-1" />
                {apiKey ? 'API Key Set' : 'Set Gemini Key'}
              </button>
              <button
                onClick={() => {
                  const log = localStorage.getItem('pomodoro_ai_log');
                  if (log) downloadAiLog(log);
                  else alert("No AI logs saved yet.");
                }}
                className="text-gray-500 hover:text-gray-300 text-xs flex items-center"
                title="Download AI Log"
              >
                <Upload className="w-3 h-3 mr-1" />
                Save AI Log
              </button>
            </div>
          </div>

          <div className="flex justify-between items-end mb-4 border-b border-gray-700 pb-3">
            <h2 className="text-lg font-bold text-gray-100 flex items-center">
              {formatDate(selectedDate)}
            </h2>

            <button
              onClick={() => generateSummary(dateEntries, formatDate(selectedDate))}
              disabled={isGenerating}
              className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1.5 rounded text-sm flex items-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Sparkles className="w-4 h-4 mr-1.5" />
              {isGenerating ? 'Analyzing...' : 'Generate AI Summary'}
            </button>
          </div>

          {/* API Key Modal */}
          {showKeyInput && (
            <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
              <div className="bg-gray-800 border border-gray-600 p-4 rounded-lg w-full max-w-sm">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-bold text-gray-200">Set Gemini API Key</h3>
                  <button onClick={() => setShowKeyInput(false)} className="text-gray-400 hover:text-white"><X className="w-4 h-4" /></button>
                </div>
                <p className="text-xs text-gray-400 mb-3">
                  Enter your Google Gemini API Key to enable AI summaries. The key is stored locally in your browser.
                </p>
                <input
                  type="password"
                  placeholder="Paste API Key here..."
                  className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white mb-3 text-sm focus:border-blue-500 focus:outline-none"
                  defaultValue={apiKey}
                  id="apiKeyInput"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') saveApiKey(e.target.value);
                  }}
                />
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => setShowKeyInput(false)}
                    className="px-3 py-1.5 text-xs text-gray-300 hover:bg-gray-700 rounded"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => {
                      const input = document.getElementById('apiKeyInput');
                      if (input) saveApiKey(input.value);
                    }}
                    className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 text-xs rounded"
                  >
                    Save Key
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Summary Section */}
          {summaries[formatDate(selectedDate)] && (
            <div className="mb-4 bg-purple-900/20 border border-purple-500/30 rounded-lg p-4">
              <h3 className="text-purple-300 font-semibold mb-2 flex items-center">
                <Sparkles className="w-4 h-4 mr-2" />
                Daily Summary
              </h3>
              <div className="text-gray-300 text-sm">
                <Markdown content={summaries[formatDate(selectedDate)]} />
              </div>
            </div>
          )}

          <div className="space-y-1">
            {dateEntries.map((entry, idx) => (
              <div key={idx} className="border-l-4 border-blue-500 pl-2 py-1 bg-gray-900/50 rounded hover:bg-gray-900 transition-colors">
                <div className="flex items-start">
                  <span className="font-mono text-xs text-gray-500 mr-2 mt-0.5">
                    [{formatTime(entry.timestamp)}]
                  </span>
                  {entry.tag && (
                    <span className="text-xs font-semibold text-blue-400 mr-2 mt-0.5">
                      ({entry.tag})
                    </span>
                  )}
                  <span className="text-sm text-gray-300 flex-1">
                    {entry.note}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={() => { setSelectedDate(null); setView('all'); }}
            className="mt-4 w-full bg-gray-700 text-white py-2 px-4 rounded-lg hover:bg-gray-600 text-sm"
          >
            Back to All Entries
          </button>
        </div>
      </div>
    );
  }

  if (view === 'overview') {
    return (
      <div className="max-w-4xl mx-auto p-2 bg-gray-900 min-h-screen">
        <div className="bg-gray-800 rounded-lg shadow-lg p-3 border border-gray-700">
          <h2 className="text-xl font-bold mb-4 text-gray-100 flex items-center border-b border-gray-700 pb-2">
            <Calendar className="w-6 h-6 mr-2" />
            Select a Date to Review
          </h2>

          {dates.length === 0 ? (
            <p className="text-gray-500 text-center py-6">No entries found.</p>
          ) : (
            <div className="space-y-4">
              {Object.keys(groupedDates).sort((a, b) => b - a).map(year => (
                <div key={year}>
                  <div className="sticky top-0 bg-gray-800 py-1 z-10">
                    <h3 className="text-lg font-bold text-blue-400">{year}</h3>
                  </div>
                  {Object.keys(groupedDates[year]).map(month => {
                    const monthDates = groupedDates[year][month];
                    return (
                      <div key={month} className="mb-3 ml-2">
                        <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">{month}</h4>
                        <div className="grid grid-cols-1 gap-2">
                          {monthDates.map((date) => {
                            const globalIndex = dates.indexOf(date);
                            const count = getEntriesForDate(date).length;
                            return (
                              <button
                                key={date}
                                onClick={() => handleDateSelect(date)}
                                className="group flex items-center justify-between p-2 bg-gray-900 hover:bg-gray-700 rounded border border-gray-700 hover:border-blue-500 transition-all text-left"
                              >
                                <div className="flex items-center">
                                  <span className="font-mono text-sm text-gray-600 group-hover:text-blue-400 w-8">
                                    {(globalIndex + 1).toString().padStart(2, '0')}
                                  </span>
                                  <span className="text-gray-200 text-sm font-medium">
                                    {formatDate(date)}
                                  </span>
                                </div>
                                <span className="text-xs bg-gray-800 px-2 py-0.5 rounded text-gray-400 group-hover:text-white">
                                  {count}
                                </span>
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          )}

          <button
            onClick={() => setView('all')}
            className="mt-4 w-full bg-gray-700 text-white py-2 px-4 rounded-lg hover:bg-gray-600 text-sm"
          >
            View All Entries
          </button>
        </div>
      </div >
    );
  }

  // Tracker/All Entries View
  return (
    <div className="max-w-4xl mx-auto p-2 bg-gray-900 min-h-screen">
      <div className="bg-gray-800 rounded-lg shadow-lg p-3 border border-gray-700">
        <div className="flex items-center justify-between mb-2 border-b border-gray-700 pb-2">
          <h1 className="text-xl font-bold text-gray-100 flex items-center">
            <Clock className="w-6 h-6 mr-2" />
            All Entries
          </h1>
          <button
            onClick={() => setView('overview')}
            className="bg-blue-600 text-white py-1 px-3 rounded hover:bg-blue-700 font-medium flex items-center text-xs"
          >
            <Calendar className="w-3 h-3 mr-1" />
            Review by Date
          </button>
        </div>

        {entries.length === 0 ? (
          <p className="text-gray-500 text-center py-6">No entries found.</p>
        ) : (
          <div className="space-y-4">
            {dates.map(date => {
              const dateEntries = getEntriesForDate(date);
              const dateObj = new Date(date);
              const dateHeader = dateObj.toLocaleDateString('en-US', {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric'
              });

              return (
                <div key={date}>
                  <h3 className="text-sm font-bold text-blue-400 bg-gray-900/50 px-2 py-1 rounded mb-1 border-l-2 border-blue-500">
                    {dateHeader}
                  </h3>
                  <div className="space-y-0.5 pl-2">
                    {dateEntries.map((entry, idx) => (
                      <div key={idx} className="font-mono text-xs text-gray-300 p-1 hover:bg-gray-900 rounded flex items-start">
                        <span className="text-gray-500 mr-2 whitespace-nowrap">
                          [{formatTime(entry.timestamp)}]
                        </span>
                        {entry.tag && <span className="text-blue-400 font-semibold mr-2 whitespace-nowrap">({entry.tag})</span>}
                        <span className="text-gray-300">{entry.note}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
        <p className="text-xs text-gray-600 mt-4 text-center border-t border-gray-800 pt-2">
          Data is processed locally. Entries are sent to Google Gemini only when you click "Generate AI Summary".
        </p>
      </div>
    </div>
  );
};
```