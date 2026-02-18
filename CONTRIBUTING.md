# Contributing to OpenClaw Production Guide

First off, thank you for considering contributing! This guide gets better when the community shares their knowledge.

## How to Contribute

### 1. Share Your Case Study

Have a different production setup? Share it!

**What we're looking for:**
- Your use case (what you use OpenClaw for)
- Your configuration
- Your results (costs, performance)
- What worked, what didn't

**How to submit:**
1. Fork this repo
2. Create file in `06-community/case-studies/`
3. Use template below
4. Submit pull request

**Template:**
```markdown
# [Your Name/Company] - [Use Case]

## Setup
- **Use case:** [Brief description]
- **Workload:** [Task-intensive / Knowledge-intensive / Mixed]
- **Models:** [Which models for what]
- **Monthly cost:** [Before → After]

## Configuration
[Key config decisions]

## Results
[What worked, what didn't]

## Lessons Learned
[What you'd do differently]
```

### 2. Suggest Optimizations

Found something that works better? Share it!

**Process:**
1. Test it in production first (we don't want theoretical advice)
2. Document results with numbers
3. Open pull request with details

**We'll merge if:**
- ✅ Tested in real production
- ✅ Numbers/evidence provided
- ✅ Clear benefit shown

### 3. Fix Errors or Outdated Info

Spotted a mistake? OpenClaw updated and something changed?

**Just submit a PR.**

No need to ask permission. If it's clearly an error, we'll merge quickly.

### 4. Improve Documentation

- Better explanations
- More examples
- Clearer instructions
- Fixed typos

**All welcome. Submit PR.**

## What We Don't Want

### ❌ Theoretical Advice

"I think you could save 90% by doing X"

→ Have you tested it? If not, test first, then share.

### ❌ Vendor Promotion

"Use [My Company]'s service instead"

→ This guide is vendor-neutral. Keep it that way.

### ❌ Dogmatic Recommendations

"Everyone should use Haiku"

→ This guide is about nuance. Show when something works AND when it doesn't.

### ❌ Incomplete Case Studies

"I saved 50% on costs!"

→ How? What was your workload? What trade-offs? Share complete context.

## Style Guidelines

### Writing Style

- **Direct and practical** (not academic)
- **Honest about trade-offs** (not selling anything)
- **Evidence-based** (numbers > opinions)
- **Examples over theory** (show, don't just tell)

### Format

- Use markdown headings properly (H1 for title, H2 for sections)
- Code blocks with syntax highlighting
- Tables for comparisons
- Real examples > hypothetical ones

### Tone

**Good:**
> "I tested Haiku on 12 tasks. It worked for 3, failed for 6. Here's why..."

**Bad:**
> "Haiku is amazing, everyone should use it!"

**Good:**
> "This optimization saved me $15/month. It works if your workload is X, but not if it's Y."

**Bad:**
> "This will save you tons of money!"

## Pull Request Process

1. **Fork the repo**
2. **Create a branch** (`git checkout -b feature/your-contribution`)
3. **Make your changes**
4. **Test if applicable** (configs, scripts)
5. **Commit with clear message**
6. **Push to your fork**
7. **Open pull request**

### PR Checklist

- [ ] Changes tested (if code/config)
- [ ] Numbers/evidence provided (if claiming results)
- [ ] Writing follows style guidelines
- [ ] No vendor promotion
- [ ] No broken links

### Review Process

- I'll review PRs weekly (usually faster)
- If it's clearly helpful, I'll merge quickly
- If it needs discussion, I'll comment
- If it doesn't fit, I'll explain why

## Questions?

Not sure if your contribution fits? **Open an issue first.** Let's discuss.

---

## Code of Conduct

**Be respectful, be honest, be helpful.**

- ✅ Disagree with ideas (with evidence)
- ❌ Don't attack people
- ✅ Share what didn't work for you
- ❌ Don't claim your way is the only way

**This is a collaborative knowledge base, not a debate club.**

---

## License

By contributing, you agree your contributions will be licensed under MIT (same as the repo).

---

**Thank you for helping make this guide better!**
