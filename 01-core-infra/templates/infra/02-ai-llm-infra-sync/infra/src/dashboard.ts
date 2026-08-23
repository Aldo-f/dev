import React from 'react';
import { render, Box, Text, Newline } from 'ink';
import { readJson } from './readers/json-reader.js';

interface ProviderInfo {
  name: string;
  count: number;
}

const Dashboard = () => {
  const [providers, setProviders] = React.useState<ProviderInfo[]>([]);

  React.useEffect(() => {
    (async () => {
      const poolPath = `${process.env.HOME}/dev/02-ai-llm-infra-sync/credential-pool.json`;
      const data = await readJson(poolPath);
      const credPool = data?.providers || {};
      const list: ProviderInfo[] = Object.entries(credPool).map(([k, v]) => ({
        name: k,
        count: (v as any[]).length,
      }));
      setProviders(list);
    })();
  }, []);

  return (
    <Box flexDirection="column">
      <Text bold>🛠️ LLM‑Infra‑Sync Dashboard</Text>
      <Newline />
      {providers.map(p => (
        <Text key={p.name}>● {p.name}: {p.count} key(s)</Text>
      ))}
      <Newline />
      <Text>Press Ctrl+C to exit.</Text>
    </Box>
  );
};

render(<Dashboard />);
