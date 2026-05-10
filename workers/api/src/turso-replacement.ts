"""Turso-based replacement for KV namespace operations."""

const TURSO_URL = "https://futures-kenan-ai.aws-eu-west-1.turso.io/v2/pipeline";
const TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3Nzc3OTUxNjEsImlkIjoiMDE5ZGVjZDktMjcwMS03MDlhLTk2NmQtOTYzMDhhM2E0NmZkIiwicmlkIjoiZDZmZGRkMzktMDIxYS00M2RmLWJjNzAtOTc2MTc5ODkzYjMyIn0.K90FTlIMI4Q95gmF3CM9ope3zIAJ86ADMj3iKHTKUgFS2ED43o5w4C0S7OeMifR6-d-xrH4cnRYDl7yYRlzMBw";

export class TursoKV {
  async get(key: string): Promise<string | null> {
    try {
      const response = await fetch(TURSO_URL, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${TURSO_TOKEN}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          requests: [{
            type: 'execute',
            stmt: {
              sql: 'SELECT value FROM kv_store WHERE key = ?',
              args: [{ type: 'text', value: key }]
            }
          }]
        })
      });
      
      const data = await response.json();
      const rows = data?.results?.[0]?.response?.result?.rows || [];
      return rows.length > 0 ? rows[0][0]?.value : null;
    } catch (e) {
      console.error(`Turso get error for ${key}:`, e);
      return null;
    }
  }
  
  async put(key: string, value: string): Promise<void> {
    try {
      await fetch(TURSO_URL, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${TURSO_TOKEN}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          requests: [{
            type: 'execute',
            stmt: {
              sql: 'INSERT OR REPLACE INTO kv_store (key, value, updated_at) VALUES (?, ?, datetime("now"))',
              args: [
                { type: 'text', value: key },
                { type: 'text', value: value }
              ]
            }
          }]
        })
      });
    } catch (e) {
      console.error(`Turso put error for ${key}:`, e);
    }
  }
}
