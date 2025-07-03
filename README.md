## What is Seldon?

Seldon is a self-improving AI coding assistant that learns from failures and successes. It tracks:
- Execution history with prompt versions
- Learned patterns from errors
- User-specific terminology
- Success/failure rates

## Key Commands to Understand Seldon

When starting a new session, run these commands in order:

```bash
# 1. Check current learning state
./seldon stats

# 2. See what patterns have been learned
./seldon prompt

# 3. Check execution history
./seldon history

# 4. See prompt evolution
./seldon evolution

# 5. Analyze patterns
./seldon analyze

# 6. Check user-specific terms
cat .seldon/user_language/dictionary.json
```

## Critical Rules

1. **NEVER DELETE .seldon/** - Contains irreplaceable learning history
2. **Do EXACTLY what's asked** - No overzealous features
3. **Test in isolation** - Use test_helper.py, not rm -rf

## Key Files

- `seldon` - Main executable
- `.seldon/` - Learning data (PRECIOUS!)
- `test_seldon_features.py` - Test suite
- `test_helper.py` - Isolated test environments
- `.seldon/learnings/meta_patterns.txt` - High-level learnings

## How to Continue Development

1. Always use `./seldon execute --task "..."` to track new work
2. Use `./seldon reflect` after attempts
3. Check `./seldon analyze --apply` periodically

## Understanding Past Decisions

Read these to understand why things are the way they are:
- `.seldon/learnings/meta_patterns.txt` - Design decisions
- `.seldon/executions/tracking.json` - What was tried
- `jj log` - Development history

## Current Success Rate

Run `./seldon stats` to see current learning metrics. As of last update, we had ~50% success rate with continuous improvement.
