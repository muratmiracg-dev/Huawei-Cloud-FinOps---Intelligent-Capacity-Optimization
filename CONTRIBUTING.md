# Contributing

## Development workflow

1. Create a focused branch.
2. Install development dependencies with `python -m pip install -e ".[dev]"`.
3. Regenerate demo data only through `scripts/generate_demo_data.py`.
4. Run `make lint`, `make coverage`, `make analyze`, and `make validate`.
5. Explain cost, capacity, security, and rollback impact in the pull request.

## Decision-engine changes

Every new optimization rule must include:

- a measurable signal,
- a documented threshold,
- an explicit exclusion or safety constraint,
- risk and confidence behavior,
- tests for positive and negative cases,
- a statement describing whether savings can stack with other rules.

Do not add a rule that mutates resources automatically. Action execution is
outside the read-only decision engine and requires a separate approval design.

## Data changes

Never commit real bills, account identifiers, AK/SK credentials, tokens, email
addresses, or customer resource names. Synthetic fixtures must be deterministic
and clearly labeled.

## Documentation

Update architecture, methodology, runbooks, and portfolio metrics when behavior
or demo output changes.
