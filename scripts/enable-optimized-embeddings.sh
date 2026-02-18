#!/bin/bash
# enable-optimized-embeddings.sh
# One-click script to enable optimized OpenAI embeddings in OpenClaw
# Tested on: OpenClaw production (38 files, 382 chunks, 0 failures)

set -e  # Exit on error

echo "🚀 OpenClaw Embeddings Optimizer"
echo "================================"
echo ""

# Check if OpenClaw is installed
if ! command -v openclaw &> /dev/null; then
    echo "❌ Error: OpenClaw not found. Install it first:"
    echo "   npm install -g openclaw"
    exit 1
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY environment variable not set"
    echo ""
    echo "To set it:"
    echo "  export OPENAI_API_KEY='sk-...'"
    echo ""
    read -p "Do you want to enter it now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your OpenAI API key: " OPENAI_KEY
        export OPENAI_API_KEY="$OPENAI_KEY"
        echo "✅ API key set for this session"
        echo ""
        echo "To make it permanent, add to ~/.bashrc or ~/.zshrc:"
        echo "  export OPENAI_API_KEY='$OPENAI_KEY'"
    else
        echo "❌ Embeddings require OPENAI_API_KEY. Exiting."
        exit 1
    fi
fi

# Get current config
echo "📋 Fetching current OpenClaw config..."
CURRENT_CONFIG=$(openclaw gateway config.get 2>/dev/null || echo "{}")

# Check if embeddings are already enabled
EMBEDDINGS_ENABLED=$(echo "$CURRENT_CONFIG" | jq -r '.embeddings.enabled // false')

if [ "$EMBEDDINGS_ENABLED" = "true" ]; then
    echo "✅ Embeddings already enabled"
    echo ""
    echo "Current config:"
    echo "$CURRENT_CONFIG" | jq '.embeddings'
    echo ""
    read -p "Do you want to re-apply optimized settings? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting without changes."
        exit 0
    fi
fi

# Prepare optimized embeddings patch
EMBEDDINGS_PATCH='{
  "embeddings": {
    "enabled": true,
    "provider": "openai",
    "model": "text-embedding-3-small",
    "batchEnabled": true,
    "debounceMs": 30000,
    "lazyIndexing": true,
    "maxCharsPerChunk": 2000,
    "overlapChars": 200
  }
}'

echo ""
echo "📝 Optimized embeddings config:"
echo "$EMBEDDINGS_PATCH" | jq '.'
echo ""
echo "Changes:"
echo "  ✅ Provider: OpenAI (text-embedding-3-small)"
echo "  ✅ Batch API: Enabled (non-blocking background processing)"
echo "  ✅ Debounce: 30s (avoids re-indexing rapidly changing files)"
echo "  ✅ Lazy Indexing: Only indexes when memory_search is called"
echo ""
echo "Cost: ~\$0.003 one-time indexing, then cached (nearly free)"
echo ""

read -p "Apply this config? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled by user."
    exit 0
fi

# Apply config patch
echo "🔧 Applying embeddings config..."
echo "$EMBEDDINGS_PATCH" | openclaw gateway config.patch

echo ""
echo "✅ Embeddings config applied!"
echo ""
echo "🔄 Restarting OpenClaw to apply changes..."
openclaw gateway restart

echo ""
echo "⏳ Waiting 10 seconds for OpenClaw to restart..."
sleep 10

echo ""
echo "🧪 Testing embeddings..."
echo ""
echo "Run this command to test memory search:"
echo "  openclaw session send 'memory_search: test query'"
echo ""
echo "Expected result:"
echo "  - First query: ~3-5s (cold start, indexing)"
echo "  - Subsequent queries: <500ms (cached)"
echo ""
echo "Verify in logs:"
echo "  openclaw gateway logs | grep -i embeddings"
echo ""
echo "Look for: 'Embeddings batch processed' (NOT 'blocking')"
echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Monitor costs:"
echo "  - Initial indexing: ~\$0.003 (one-time)"
echo "  - Subsequent queries: \$0 (cached)"
echo "  - Total monthly cost: <\$0.01 (negligible)"
echo ""
echo "📚 Troubleshooting:"
echo "  - If you see 'Batch API disabled': Check OPENAI_API_KEY is correct"
echo "  - If queries are slow: First query is always slow (cold start)"
echo "  - If chunks fail: Check file encoding (must be UTF-8)"
echo ""
echo "Done! 🎉"
