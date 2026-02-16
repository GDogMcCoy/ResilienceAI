# 🎯 Archia Cloud Quick Reference

## API Key
```
ask_ouIAvAYrMqb8LnlJxfDeU3hvOdEkOpA3EGmiS0XlWvc=
```

## Console Access
**URL:** https://console.archia.app  
**API Endpoint:** https://api.archia.app/v1

## Quick Deploy
```bash
cd /root/.openclaw/workspace/ResilienceAI
./deploy-to-archia.sh
```

## Manual Deploy
```bash
# 1. Set API key
export ARCHIA_API_KEY="ask_ouIAvAYrMqb8LnlJxfDeU3hvOdEkOpA3EGmiS0XlWvc="

# 2. Deploy agent configuration
curl -X POST https://api.archia.app/v1/agents/deploy \
  -H "Authorization: Bearer $ARCHIA_API_KEY" \
  -H "Content-Type: application/json" \
  -d @archia/archia.toml

# 3. Test query
curl -X POST https://api.archia.app/v1/agents/resilienceai/query \
  -H "Authorization: Bearer $ARCHIA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which Missouri counties are most vulnerable?"
  }'
```

## Dashboard Setup
```bash
# 1. Start Streamlit
streamlit run app/dashboard.py

# 2. Open http://localhost:8501

# 3. In the sidebar, enter:
#    Archia Endpoint: https://api.archia.app/v1
#    API Key: ask_ouIAvAYrMqb8LnlJxfDeU3hvOdEkOpA3EGmiS0XlWvc=
```

## Demo Queries

### Geographic
- "Which Missouri counties are most vulnerable to flooding?"
- "Show me the highest risk counties in Texas"
- "What counties in Florida have the worst hurricane exposure?"

### Temporal
- "Where are disasters accelerating fastest?"
- "Which counties have increasing flood frequency?"

### Infrastructure
- "Which counties have zero hospital redundancy?"
- "Where are the worst EMS deserts?"

### Compound Risk
- "Show me compound risk hotspots"
- "Which counties are high on 3+ risk dimensions?"

### Interventions
- "What single intervention would most reduce risk in Jackson County?"
- "Which counties would benefit most from adding a hospital?"

### Comparison
- "Compare St. Louis County to its peers"
- "How does Boone County rank in Missouri?"

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/agents/resilienceai/query` | POST | Natural language query |
| `/v1/agents/resilienceai/tools` | GET | List available tools |
| `/v1/agents/resilienceai/status` | GET | Agent health status |
| `/health` | GET | API health check |

## Example API Response
```json
{
  "response": "The most vulnerable Missouri counties are...",
  "tool_calls": [
    {
      "tool": "query_counties",
      "params": {"state": "MO", "max_results": 10}
    }
  ],
  "data": [...],
  "confidence": 0.95
}
```

## Troubleshooting

### Connection Issues
```bash
# Test API connectivity
curl -H "Authorization: Bearer ask_ouIAvAYrMqb8LnlJxfDeU3hvOdEkOpA3EGmiS0XlWvc=" \
  https://api.archia.app/v1/health
```

### Agent Not Responding
1. Check deployment status in Archia Console
2. Verify API key is correct
3. Check agent logs: `archia logs resilienceai`

### Dashboard Can't Connect
1. Verify Archia endpoint URL
2. Check API key is entered correctly
3. Ensure network allows HTTPS to api.archia.app

## Files Location
```
/root/.openclaw/workspace/ResilienceAI/
├── archia/
│   ├── archia.toml          # Agent configuration
│   ├── mcp-servers.toml     # MCP server definitions
│   └── deployment.yaml      # K8s deployment
├── app/
│   └── dashboard.py         # Streamlit dashboard
├── src/
│   └── archia_client.py     # Python API client
├── deploy-to-archia.sh      # Deployment script
└── .env.archia              # Environment variables
```

## Support
- **Archia Docs:** https://docs.archia.app
- **Console:** https://console.archia.app
- **API Reference:** https://docs.archia.app/api

---

**Ready for hackathon demo! 🚀**
